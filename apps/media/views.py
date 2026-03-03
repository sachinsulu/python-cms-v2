import logging

from django.conf import settings

from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.core.paginator import Paginator

from apps.core.mixins import CMSPermissionMixin

from .models import MediaAsset

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class MediaUploadView(View):
    """
    AJAX endpoint — upload a file and create a MediaAsset.
    Returns JSON: {id, url, thumbnail_url, alt_text, file_type}
    """

    def post(self, request):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return JsonResponse({'error': 'No file provided'}, status=400)

        max_size = getattr(settings, 'MEDIA_MAX_FILE_SIZE', 10 * 1024 * 1024)
        allowed_exts = getattr(settings, 'MEDIA_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'webp'])

        if uploaded.size > max_size:
            return JsonResponse({'error': f'File too large. Max size is {max_size // (1024*1024)}MB.'}, status=400)

        ext = uploaded.name.rsplit('.', 1)[-1].lower() if '.' in uploaded.name else ''
        if ext not in allowed_exts:
            return JsonResponse({'error': f'File type not allowed. Allowed: {", ".join(allowed_exts)}'}, status=400)

        alt_text = request.POST.get('alt_text', '').strip()

        asset = MediaAsset(
            file=uploaded,
            alt_text=alt_text,
            uploaded_by=request.user,
        )
        asset.save()

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
    AJAX endpoint — returns an HTML fragment of all media assets for the
    library modal.  Supports ?type=image to filter by file_type.
    """

    def get(self, request):
        qs = MediaAsset.objects.filter(is_active=True)  # ← changed

        file_type = request.GET.get('type')
        if file_type in ('image', 'file', 'video'):
            qs = qs.filter(file_type=file_type)

        html = render_to_string('media/library_grid.html', {
            'assets': qs[:100],
        }, request=request)

        return JsonResponse({'html': html})


class MediaAdminListView(CMSPermissionMixin, View):
    """Full-page admin list view for the media library."""
    permission_required = 'media.view_mediaasset'

    PAGE_SIZE = 60

    def get(self, request):
        qs        = MediaAsset.objects.select_related('uploaded_by').order_by('-created_at')
        file_type = request.GET.get('type')
        if file_type in ('image', 'file', 'video'):
            qs = qs.filter(file_type=file_type)

        paginator = Paginator(qs, self.PAGE_SIZE)
        page      = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'media/admin_list.html', {
            'assets':      page.object_list,
            'page_obj':    page,
            'paginator':   paginator,
            'model_key':   'media',
            'active_filter': file_type or 'all',
        })
