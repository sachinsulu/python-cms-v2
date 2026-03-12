from django.test import TestCase
from apps.articles.models import Article
from apps.blog.models import Blog
from apps.core.models import GlobalSlug


class GlobalSlugTests(TestCase):

    def _make_article(self, slug, title='T'):
        return Article.objects.create(title=title, slug=slug, content='x')

    def test_globalslug_created_on_save(self):
        self._make_article('my-article')
        self.assertTrue(GlobalSlug.objects.filter(slug='my-article').exists())

    def test_globalslug_model_name_correct(self):
        self._make_article('another-article')
        gs = GlobalSlug.objects.get(slug='another-article')
        self.assertEqual(gs.model_name, 'Article')

    def test_globalslug_removed_on_delete(self):
        article = self._make_article('delete-me')
        article.delete()
        self.assertFalse(GlobalSlug.objects.filter(slug='delete-me').exists())

    def test_globalslug_upserts_on_slug_change(self):
        article = self._make_article('old-slug')
        article.slug = 'new-slug'
        article.save()
        self.assertFalse(GlobalSlug.objects.filter(slug='old-slug').exists())
        self.assertTrue(GlobalSlug.objects.filter(slug='new-slug').exists())

    def test_cross_model_conflict_detected(self):
        Blog.objects.create(title='B', slug='shared-slug')
        from apps.articles.forms import ArticleForm
        form = ArticleForm(data={
            'title': 'A', 'slug': 'shared-slug',
            'content': 'x', 'is_active': True,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)

    def test_editing_own_slug_does_not_conflict(self):
        article = self._make_article('keep-my-slug')
        from apps.articles.forms import ArticleForm
        form = ArticleForm(
            data={'title': 'T', 'slug': 'keep-my-slug', 'content': 'x', 'is_active': True},
            instance=article,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_is_slug_taken_single_query(self):
        from apps.core.registry import cms_registry
        self._make_article('exists-slug')
        with self.assertNumQueries(1):
            result = cms_registry.is_slug_taken('exists-slug')
        self.assertTrue(result)
