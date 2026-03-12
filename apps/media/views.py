"""
apps/media/views.py
"""
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View

from apps.core.mixins import CMSPermissionMixin
from .models import MediaAsset
from .validators import UploadValidationError, validate_upload

logger = logging.getLogger(__name__)

LIBRARY_PAGE_SIZE = 48


@method_decorator(login_required, name='dispatch')
class MediaUploadView(View):
    """
    AJAX endpoint — upload a file and create a MediaAsset.

    Security layers (in order):
      1. File size cap        — settings.MEDIA_MAX_FILE_SIZE
      2. Extension allow-list — settings.MEDIA_ALLOWED_EXTENSIONS
      3. SVG hard-block       — SVG can embed <script> → XSS if self-hosted
      4. Magic-byte sniffing  — detects renamed files for common image types
    """

    def post(self, request):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return JsonResponse({'error': 'No file provided.'}, status=400)

        allowed_exts = getattr(
            settings,
            'MEDIA_ALLOWED_EXTENSIONS',
            ['jpg', 'jpeg', 'png', 'webp'],
        )

        try:
            validate_upload(uploaded, allowed_exts)
        except UploadValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        alt_text = request.POST.get('alt_text', '').strip()

        try:
            asset = MediaAsset(
                file=uploaded,
                alt_text=alt_text,
                uploaded_by=request.user,
            )
            asset.save()
        except Exception:
            logger.exception(
                'MediaAsset save failed — user=%s file=%s',
                request.user,
                uploaded.name,
            )
            return JsonResponse(
                {'error': 'Upload failed due to a server error. Please try again.'},
                status=500,
            )

        return JsonResponse({
            'id':            asset.pk,
            'url':           asset.url,
            'thumbnail_url': asset.thumbnail_url,
            'alt_text':      asset.alt_text,
            'file_type':     asset.file_type,
            'filename':      str(asset),
        })


@method_decorator(login_required, name='dispatch')
class MediaLibraryView(View):
    """
    AJAX endpoint — returns an HTML fragment for the picker modal.

    Fixes vs original:
      - .order_by('-created_at') added  → deterministic results on PostgreSQL
      - Paginator replaces [:100]       → unbounded slice removed

    Query params:
        type  — optional: 'image' | 'file' | 'video'
        page  — page number (default 1)

    Response JSON:
        html, has_next, has_prev, page, total
    """

    def get(self, request):
        qs = (
            MediaAsset.objects
            .filter(is_active=True)
            .order_by('-created_at')
        )

        file_type = request.GET.get('type')
        if file_type in ('image', 'file', 'video'):
            qs = qs.filter(file_type=file_type)

        paginator = Paginator(qs, LIBRARY_PAGE_SIZE)
        page = paginator.get_page(request.GET.get('page', 1))

        html = render_to_string(
            'media/library_grid.html',
            {
                'assets':   page.object_list,
                'page_obj': page,
            },
            request=request,
        )

        return JsonResponse({
            'html':     html,
            'has_next': page.has_next(),
            'has_prev': page.has_previous(),
            'page':     page.number,
            'total':    paginator.count,
        })


class MediaAdminListView(CMSPermissionMixin, View):
    """Full-page admin list view for the media library. Unchanged."""
    permission_required = 'media.view_mediaasset'
    PAGE_SIZE = 60

    def get(self, request):
        qs = MediaAsset.objects.select_related('uploaded_by').order_by('-created_at')

        file_type = request.GET.get('type')
        if file_type in ('image', 'file', 'video'):
            qs = qs.filter(file_type=file_type)

        paginator = Paginator(qs, self.PAGE_SIZE)
        page = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'media/admin_list.html', {
            'assets':        page.object_list,
            'page_obj':      page,
            'paginator':     paginator,
            'model_key':     'media',
            'active_filter': file_type or 'all',
        })
