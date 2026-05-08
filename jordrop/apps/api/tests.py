import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.games.models import Game
from apps.wiki.models import Page, PageRevision, EditRequest


class FakeGroqResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode('utf-8')


class GroqChatAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(GROQ_API_KEY='')
    def test_chat_requires_groq_api_key(self):
        response = self.client.post('/api/ai/chat/', {'message': 'hello'}, format='json')

        self.assertEqual(response.status_code, 503)
        self.assertIn('GROQ_API_KEY', response.data['detail'])

    @override_settings(
        GROQ_API_KEY='test-key',
        GROQ_MODEL='llama-3.1-8b-instant',
        GROQ_CHAT_COMPLETIONS_URL='https://api.groq.com/openai/v1/chat/completions',
        GROQ_REQUEST_TIMEOUT=20,
    )
    @patch('apps.api.views.urlopen')
    def test_chat_proxies_message_to_groq(self, mock_urlopen):
        mock_urlopen.return_value = FakeGroqResponse({
            'choices': [{'message': {'content': 'Watch the economy and map control.'}}],
        })

        response = self.client.post('/api/ai/chat/', {'message': 'How do I improve?'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['answer'], 'Watch the economy and map control.')
        self.assertEqual(response.data['model'], 'llama-3.1-8b-instant')

        groq_request = mock_urlopen.call_args.args[0]
        payload = json.loads(groq_request.data.decode('utf-8'))
        self.assertEqual(payload['model'], 'llama-3.1-8b-instant')
        self.assertEqual(payload['messages'][-1]['content'], 'How do I improve?')
        self.assertEqual(groq_request.get_header('Authorization'), 'Bearer test-key')


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
