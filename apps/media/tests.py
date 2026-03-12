from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .validators import (
    validate_extension, validate_file_size, validate_magic_bytes,
    UploadValidationError,
)


class ValidateExtensionTests(TestCase):

    def test_allowed_extension_passes(self):
        self.assertEqual(validate_extension('photo.jpg', ['jpg', 'png']), 'jpg')

    def test_disallowed_extension_raises(self):
        with self.assertRaises(UploadValidationError):
            validate_extension('malware.exe', ['jpg', 'png'])

    def test_svg_blocked_even_if_in_allowed_list(self):
        with self.assertRaises(UploadValidationError) as ctx:
            validate_extension('icon.svg', ['jpg', 'png', 'svg'])
        self.assertIn('SVG', str(ctx.exception))

    def test_no_extension_raises(self):
        with self.assertRaises(UploadValidationError):
            validate_extension('noextension', ['jpg'])

    def test_case_insensitive(self):
        self.assertEqual(validate_extension('photo.JPG', ['jpg']), 'jpg')


class ValidateFileSizeTests(TestCase):

    def test_within_limit_passes(self):
        f = SimpleUploadedFile('t.jpg', b'x' * 1024)
        validate_file_size(f, 10 * 1024 * 1024)  # no exception

    def test_over_limit_raises(self):
        f = SimpleUploadedFile('t.jpg', b'x' * (11 * 1024 * 1024))
        with self.assertRaises(UploadValidationError) as ctx:
            validate_file_size(f, 10 * 1024 * 1024)
        self.assertIn('10 MB', str(ctx.exception))


class ValidateMagicBytesTests(TestCase):

    def test_valid_jpeg_passes(self):
        content = b'\xff\xd8\xff\xe0' + b'\x00' * 12
        f = SimpleUploadedFile('photo.jpg', content)
        validate_magic_bytes(f, 'jpg')  # no exception

    def test_mismatched_magic_raises(self):
        # PNG bytes renamed as JPEG
        content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 8
        f = SimpleUploadedFile('fake.jpg', content)
        with self.assertRaises(UploadValidationError):
            validate_magic_bytes(f, 'jpg')

    def test_file_pointer_reset_after_read(self):
        content = b'\xff\xd8\xff\xe0' + b'\x00' * 12
        f = SimpleUploadedFile('photo.jpg', content)
        validate_magic_bytes(f, 'jpg')
        self.assertEqual(f.tell(), 0)

    def test_video_skips_magic_check(self):
        f = SimpleUploadedFile('clip.mp4', b'garbage bytes')
        validate_magic_bytes(f, 'mp4')  # no exception
