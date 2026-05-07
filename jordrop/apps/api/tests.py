from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.games.models import Game
from apps.wiki.models import Page, PageRevision, EditRequest


class APIEditRequestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.game = Game.objects.create(name='Valorant', slug='valorant-api')
        self.page = Page.objects.create(game=self.game, title='Agents', slug='agents-api')
        self.contributor = User.objects.create_user('contrib', password='pass', role=User.CONTRIBUTOR)
        self.moderator = User.objects.create_user('mod', password='pass', role=User.MODERATOR)

    def test_contributor_can_create_edit_request(self):
        self.client.force_authenticate(user=self.contributor)
        response = self.client.post('/api/edit-requests/', {
            'page': self.page.pk,
            'proposed_content': 'New content here',
            'edit_summary': 'Added agents list',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(EditRequest.objects.count(), 1)

    def test_visitor_cannot_create_edit_request(self):
        visitor = User.objects.create_user('visitor', password='pass', role=User.VISITOR)
        self.client.force_authenticate(user=visitor)
        response = self.client.post('/api/edit-requests/', {
            'page': self.page.pk,
            'proposed_content': 'Visitor content',
        })
        self.assertEqual(response.status_code, 403)

    def test_moderator_can_approve(self):
        edit = EditRequest.objects.create(
            page=self.page, author=self.contributor, proposed_content='Good content'
        )
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(f'/api/edit-requests/{edit.pk}/approve/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'approved')

    def test_contributor_cannot_approve(self):
        edit = EditRequest.objects.create(
            page=self.page, author=self.contributor, proposed_content='Content'
        )
        self.client.force_authenticate(user=self.contributor)
        response = self.client.post(f'/api/edit-requests/{edit.pk}/approve/')
        self.assertEqual(response.status_code, 403)

    def test_games_endpoint_is_public(self):
        response = self.client.get('/api/games/')
        self.assertEqual(response.status_code, 200)
