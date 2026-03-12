from django.test import TestCase
from .forms import NearbyForm


class NearbyMapLinkTests(TestCase):

    def _form(self, map_link):
        return NearbyForm(data={
            'title': 'Test Place',
            'map_link': map_link,
            'distance': '500m',
            'content': '',
            'is_active': True,
        })

    def test_valid_url_accepted(self):
        self.assertTrue(self._form('https://maps.google.com/?q=beach').is_valid())

    def test_long_url_accepted(self):
        long_url = 'https://www.google.com/maps/embed?pb=' + 'x' * 400
        self.assertTrue(self._form(long_url).is_valid())

    def test_non_url_rejected(self):
        form = self._form('not a url at all')
        self.assertFalse(form.is_valid())
        self.assertIn('map_link', form.errors)

    def test_blank_map_link_is_valid(self):
        self.assertTrue(self._form('').is_valid())
