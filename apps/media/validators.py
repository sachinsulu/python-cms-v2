"""
apps/media/validators.py
========================
Centralised file-upload validators for the media library.
Pure Python — no ORM dependency — safe to unit-test in isolation.

Usage:
    from .validators import validate_upload, UploadValidationError
    try:
        validate_upload(request.FILES['file'], allowed_extensions)
    except UploadValidationError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
"""
import logging

logger = logging.getLogger(__name__)

# SVG is valid XML and can carry <script> tags.
# If served from your own domain it is a stored-XSS vector — block always.
BLOCKED_EXTENSIONS: frozenset = frozenset({'svg'})

# Magic-byte signatures keyed by lowercase extension.
# Tuple of byte-string prefixes; ANY match is sufficient.
# None = handled by a dedicated helper (_is_valid_webp).
# Missing key = no signature check for this type.
_MAGIC: dict = {
    'jpg':  (b'\xff\xd8\xff',),
    'jpeg': (b'\xff\xd8\xff',),
    'png':  (b'\x89PNG\r\n\x1a\n',),
    'gif':  (b'GIF87a', b'GIF89a'),
    'webp': None,
    'pdf':  (b'%PDF',),
    'zip':  (b'PK\x03\x04',),
}

# Extensions where magic-byte checking is skipped.
# Binary formats with many vendor variants; extension + size is sufficient
# for an authenticated CMS admin upload flow.
_SKIP_MAGIC: frozenset = frozenset({
    'mp4', 'mov', 'avi', 'mkv', 'webm',
    'doc', 'docx', 'xls', 'xlsx',
    'txt', 'csv', 'bmp', 'ico',
    'heic',  # HEIC uses the ISOBMFF container; magic bytes vary by encoder
})

_HEADER_BYTES = 16


class UploadValidationError(Exception):
    """Raised by validators; message is safe to return directly to the user."""


def validate_file_size(file, max_bytes: int) -> None:
    if file.size > max_bytes:
        mb = max_bytes // (1024 * 1024)
        raise UploadValidationError(
            f'File too large. Maximum allowed size is {mb} MB.'
        )


def validate_extension(filename: str, allowed_extensions: list) -> str:
    """Returns the validated lowercase extension, or raises UploadValidationError."""
    if '.' not in filename:
        raise UploadValidationError(
            'File has no extension. Please rename the file and try again.'
        )

    ext = filename.rsplit('.', 1)[-1].lower()

    if ext in BLOCKED_EXTENSIONS:
        raise UploadValidationError(
            f'".{ext}" files are not permitted. '
            'SVG can contain executable scripts and is blocked for security reasons.'
        )

    if ext not in [e.lower() for e in allowed_extensions]:
        allowed_display = ', '.join(f'.{e}' for e in sorted(allowed_extensions))
        raise UploadValidationError(
            f'".{ext}" is not an allowed file type. Allowed: {allowed_display}'
        )

    return ext


def validate_magic_bytes(file, ext: str) -> None:
    """
    Read the first bytes of the file and verify they match the known signature.
    Always resets the file pointer to 0 after reading.
    """
    if ext in _SKIP_MAGIC or ext not in _MAGIC:
        return

    try:
        header = file.read(_HEADER_BYTES)
        file.seek(0)
    except Exception as exc:
        logger.warning('validate_magic_bytes: could not read header ext=%s: %s', ext, exc)
        return  # fail open on unusual storage backends

    if ext == 'webp':
        if not _is_valid_webp(header):
            raise UploadValidationError(
                'File content does not match the declared ".webp" extension. Upload rejected.'
            )
        return

    signatures = _MAGIC[ext]
    if signatures and not any(header.startswith(sig) for sig in signatures):
        raise UploadValidationError(
            f'File content does not match the declared ".{ext}" extension. Upload rejected.'
        )


def _is_valid_webp(header: bytes) -> bool:
    # RIFF....WEBP — bytes 0-3 are RIFF, bytes 8-11 are WEBP
    return (
        len(header) >= 12
        and header[:4] == b'RIFF'
        and header[8:12] == b'WEBP'
    )


def validate_upload(file, allowed_extensions: list) -> str:
    """
    Master validator. Runs: size → extension → magic bytes.
    Returns the validated lowercase extension.
    Raises UploadValidationError on first failure.
    """
    from django.conf import settings
    max_bytes = getattr(settings, 'MEDIA_MAX_FILE_SIZE', 10 * 1024 * 1024)

    validate_file_size(file, max_bytes)
    ext = validate_extension(file.name, allowed_extensions)
    validate_magic_bytes(file, ext)
    return ext
