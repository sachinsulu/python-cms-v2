"""
Core Views
==========
- DashboardView
- Generic action endpoints: toggle, bulk, reorder, delete, slug check
  All read from cms_registry — no hardcoded model lists.
"""
import json
import logging
from urllib.parse import urlparse

from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.db.models import Case, When, Value, BooleanField
from django.utils.decorators import method_decorator

from .mixins import CMSPermissionMixin, SuperuserRequiredMixin
from .models import AuditLog
from .audit import log_action, log_bulk_action, get_client_ip
from .registry import cms_registry
from .cache import invalidate_dashboard_cache
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def redirect_back(request, default='/'):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return redirect(default)
    parsed = urlparse(referer)
    if parsed.netloc and parsed.netloc != request.get_host():
        return redirect(default)
    safe_path = parsed.path or default
    return redirect(safe_path)


def check_perm(request, model_class, action='change') -> bool:
    if request.user.is_superuser:
        return True
    app   = model_class._meta.app_label
    model = model_class._meta.model_name
    return request.user.has_perm(f'{app}.{action}_{model}')


# ------------------------------------------------------------------ #
# Dashboard
# ------------------------------------------------------------------ #

@method_decorator(login_required, name='dispatch')
class DashboardView(View):

    def get(self, request):
        user    = request.user
        version = cache.get('dashboard_stats_version', 1)

        stats_key   = f'dashboard_stats_{user.pk}_v{version}'
        recent_key  = f'dashboard_recent_{user.pk}_v{version}'

        stats   = cache.get(stats_key)
        recent  = cache.get(recent_key)

        if not stats:
            stats = cms_registry.get_dashboard_stats(user)
            cache.set(stats_key, stats, timeout=60)

        if not recent:
            recent = cms_registry.get_recent_items(user)
            cache.set(recent_key, recent, timeout=60)

        return render(request, 'dashboard.html', {
            'stats':          stats,
            'recent_modules': recent,
        })


# ------------------------------------------------------------------ #
# Audit log view
# ------------------------------------------------------------------ #

@method_decorator(login_required, name='dispatch')
class AuditLogView(SuperuserRequiredMixin, View):

    def get(self, request):
        logs = AuditLog.objects.select_related('user').all()[:200]
        return render(request, 'core/audit_log.html', {'logs': logs})


@login_required
@require_POST
def clear_audit_log(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    count = AuditLog.objects.count()
    AuditLog.objects.all().delete()
    messages.success(request, f'Audit log cleared ({count} entries deleted).')
    return redirect('audit_log')


# ------------------------------------------------------------------ #
# Generic action endpoints (consumed via AJAX / form POSTs)
# ------------------------------------------------------------------ #

@login_required
@require_POST
def toggle_status(request, model_key, pk):
    config = cms_registry.get(model_key)
    if not config:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    # ADD THIS GUARD
    if not config.active_field:
        return JsonResponse({'error': 'This model does not support toggling'}, status=400)

    if not check_perm(request, config.model, 'change'):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    obj     = get_object_or_404(config.model, pk=pk)
    field   = config.active_field
    current = getattr(obj, field)
    setattr(obj, field, not current)
    obj.save(update_fields=[field])
    invalidate_dashboard_cache()

    log_action(request, AuditLog.TOGGLE, obj, changes={field: {'before': current, 'after': not current}})
    return JsonResponse({'status': not current, 'message': f'"{obj}" status updated.'})


@login_required
@require_POST
def delete_object(request, model_key, pk):
    config = cms_registry.get(model_key)
    if not config:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    if not check_perm(request, config.model, 'delete'):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    obj      = get_object_or_404(config.model, pk=pk)
    obj_repr = str(obj)
    obj_id   = str(obj.pk)
    obj.delete()
    invalidate_dashboard_cache()

    # Log manually since the obj is gone
    AuditLog.objects.create(
        user        = request.user,
        action      = AuditLog.DELETE,
        model_name  = config.model.__name__,
        object_id   = obj_id,
        object_repr = obj_repr,
        ip_address  = get_client_ip(request),  # ← added
        changes     = {},
    )
    return JsonResponse({'success': True, 'message': f'"{obj_repr}" deleted.'})


@login_required
@require_POST
def bulk_action(request, model_key):
    config = cms_registry.get(model_key)
    if not config or not config.supports_bulk:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    action       = request.POST.get('action')
    selected_ids = request.POST.getlist('selected_ids')

    if not selected_ids:
        return JsonResponse({'error': 'No items selected'}, status=400)

    if action not in ('toggle', 'delete'):
        return JsonResponse({'error': 'Invalid action'}, status=400)

    required_perm = 'delete' if action == 'delete' else 'change'
    if not check_perm(request, config.model, required_perm):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    qs = config.model.objects.filter(pk__in=selected_ids)

    if action == 'toggle':
        field = config.active_field

        # ADD THIS GUARD (pairs with Fix 1)
        if not field:
            return JsonResponse({'error': 'This model does not support toggling'}, status=400)

        count = qs.count()  # ← count BEFORE update
        qs.update(**{
            field: Case(
                When(**{field: True},  then=Value(False)),
                When(**{field: False}, then=Value(True)),
                output_field=BooleanField(),
            )
        })
        log_bulk_action(request, AuditLog.BULK_TOGGLE, config.model.__name__, count, selected_ids)
        invalidate_dashboard_cache()
        return JsonResponse({'success': True, 'message': f'{count} items toggled.'})

    if action == 'delete':
        count = qs.count()
        log_bulk_action(request, AuditLog.BULK_DELETE, config.model.__name__, count, selected_ids)
        qs.delete()
        invalidate_dashboard_cache()
        return JsonResponse({'success': True, 'message': f'{count} items deleted.'})


@login_required
@require_POST
def update_order(request, model_key):
    config = cms_registry.get(model_key)
    if not config or not config.supports_sort:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    if not check_perm(request, config.model, 'change'):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    try:
        data  = json.loads(request.body)
        order = [int(i) for i in data.get('order', [])]
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    with transaction.atomic():
        objs    = config.model.objects.select_for_update().filter(pk__in=order).only('pk', 'position')
        obj_map = {obj.pk: obj for obj in objs}
        to_update = []
        for position, obj_id in enumerate(order):
            if obj_id in obj_map:
                obj_map[obj_id].position = position
                to_update.append(obj_map[obj_id])
        config.model.objects.bulk_update(to_update, ['position'])

    log_bulk_action(request, AuditLog.REORDER, config.model.__name__, len(order), order)
    return JsonResponse({'success': True})


@login_required
@require_GET
def ajax_check_slug(request, model_key):
    slug       = request.GET.get('slug', '').strip()
    exclude_id = request.GET.get('exclude_id')

    if not slug:
        return JsonResponse({'available': False, 'message': 'Slug cannot be empty'})

    # Get the exclude object if editing
    exclude_obj = None
    config = cms_registry.get(model_key)
    if config and exclude_id:
        try:
            exclude_obj = config.model.objects.get(pk=int(exclude_id))
        except (config.model.DoesNotExist, ValueError):
            pass

    taken = cms_registry.is_slug_taken(slug, exclude_obj=exclude_obj)
    return JsonResponse({
        'available': not taken,
        'message':   'Slug is available.' if not taken else 'Slug exists. Please choose another.',
    })
