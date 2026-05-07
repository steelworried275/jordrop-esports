from django.test import TestCase, Client
from django.urls import reverse

from apps.users.models import User
from apps.games.models import Game
from apps.wiki.models import Page, PageRevision, EditRequest


def make_user(username, role):
    return User.objects.create_user(username=username, password='testpass123', role=role)


class PageRevisionAutoNumberTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name='CS2', slug='cs2')
        self.user = make_user('editor', User.CONTRIBUTOR)
        self.page = Page.objects.create(game=self.game, title='Dust2', slug='dust2')

    def test_first_revision_is_number_one(self):
        rev = PageRevision.objects.create(page=self.page, author=self.user, content='Hello')
        self.assertEqual(rev.revision_number, 1)

    def test_second_revision_increments(self):
        PageRevision.objects.create(page=self.page, author=self.user, content='v1')
        rev2 = PageRevision.objects.create(page=self.page, author=self.user, content='v2')
        self.assertEqual(rev2.revision_number, 2)

    def test_content_rendered_is_set_automatically(self):
        rev = PageRevision.objects.create(page=self.page, author=self.user, content='**bold**')
        self.assertIn('<strong>', rev.content_rendered)


class EditRequestApproveTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name='Valorant', slug='valorant')
        self.contributor = make_user('contrib', User.CONTRIBUTOR)
        self.moderator = make_user('mod', User.MODERATOR)
        self.page = Page.objects.create(game=self.game, title='Agents', slug='agents')

    def test_approve_creates_revision_and_updates_page(self):
        edit = EditRequest.objects.create(
            page=self.page,
            author=self.contributor,
            proposed_content='## Agents\nList of agents.',
            edit_summary='Initial content',
        )
        revision = edit.approve(self.moderator)
        self.page.refresh_from_db()
        edit.refresh_from_db()

        self.assertEqual(edit.status, EditRequest.STATUS_APPROVED)
        self.assertEqual(edit.reviewed_by, self.moderator)
        self.assertEqual(self.page.current_revision, revision)
        self.assertEqual(revision.revision_number, 1)

    def test_reject_sets_status_and_comment(self):
        edit = EditRequest.objects.create(
            page=self.page,
            author=self.contributor,
            proposed_content='Spam content',
        )
        edit.reject(self.moderator, comment='Off-topic')
        edit.refresh_from_db()

        self.assertEqual(edit.status, EditRequest.STATUS_REJECTED)
        self.assertEqual(edit.review_comment, 'Off-topic')
        self.assertEqual(edit.reviewed_by, self.moderator)

    def test_approve_is_atomic(self):
        """Approving an edit and promoting the revision happen in one transaction."""
        edit = EditRequest.objects.create(
            page=self.page, author=self.contributor, proposed_content='Content',
        )
        edit.approve(self.moderator)
        # Both revision and page update must have persisted
        self.assertEqual(PageRevision.objects.filter(page=self.page).count(), 1)
        self.assertIsNotNone(Page.objects.get(pk=self.page.pk).current_revision)


class RestoreRevisionTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name='CS2', slug='cs2-r')
        self.user = make_user('author', User.CONTRIBUTOR)
        self.page = Page.objects.create(game=self.game, title='Mirage', slug='mirage')

    def test_apply_revision_changes_current(self):
        rev1 = PageRevision.objects.create(page=self.page, author=self.user, content='v1')
        rev2 = PageRevision.objects.create(page=self.page, author=self.user, content='v2')
        self.page.apply_revision(rev2)
        self.assertEqual(self.page.current_revision, rev2)
        # Restore to rev1
        self.page.apply_revision(rev1)
        self.page.refresh_from_db()
        self.assertEqual(self.page.current_revision, rev1)


class RBACViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(name='CS2', slug='cs2-rbac')
        self.page = Page.objects.create(game=self.game, title='Nuke', slug='nuke')
        PageRevision.objects.create(page=self.page, author=None, content='Content')
        self.page.apply_revision(self.page.revisions.first())

    def test_visitor_cannot_access_submit_edit(self):
        visitor = make_user('visitor', User.VISITOR)
        self.client.login(username='visitor', password='testpass123')
        response = self.client.get(f'/wiki/cs2-rbac/nuke/edit/')
        self.assertEqual(response.status_code, 403)

    def test_contributor_can_access_submit_edit(self):
        contrib = make_user('contrib2', User.CONTRIBUTOR)
        self.client.login(username='contrib2', password='testpass123')
        response = self.client.get(f'/wiki/cs2-rbac/nuke/edit/')
        self.assertEqual(response.status_code, 200)

    def test_visitor_cannot_access_moderation_queue(self):
        visitor = make_user('visitor2', User.VISITOR)
        self.client.login(username='visitor2', password='testpass123')
        response = self.client.get('/wiki/moderation/queue/')
        self.assertEqual(response.status_code, 403)

    def test_moderator_can_access_moderation_queue(self):
        mod = make_user('mod2', User.MODERATOR)
        self.client.login(username='mod2', password='testpass123')
        response = self.client.get('/wiki/moderation/queue/')
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_submit_edit_is_denied(self):
        response = self.client.get(f'/wiki/cs2-rbac/nuke/edit/')
        self.assertEqual(response.status_code, 403)


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(name='Valorant', slug='valorant-s')
        self.user = make_user('searcher', User.CONTRIBUTOR)
        page = Page.objects.create(game=self.game, title='Ascent Map Guide', slug='ascent')
        rev = PageRevision.objects.create(page=page, author=self.user, content='Ascent is a map.')
        page.apply_revision(rev)

    def test_search_finds_page_by_title(self):
        response = self.client.get('/search/?q=Ascent')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ascent Map Guide')

    def test_empty_query_returns_no_results(self):
        response = self.client.get('/search/?q=')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Ascent Map Guide')
