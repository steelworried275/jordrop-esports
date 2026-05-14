from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from .models import Game, Player, Team
from .services import PandaScoreClient
from .services.pandascore import PandaScoreConfigError


class PandaScoreClientTest(TestCase):
    @patch.dict('os.environ', {'PANDASCORE_API_TOKEN': 'test-token'}, clear=True)
    @patch('apps.games.services.pandascore.urlopen')
    def test_uses_game_specific_player_endpoint(self, mock_urlopen):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        response.read.return_value = b'[]'
        mock_urlopen.return_value = response

        PandaScoreClient().list_players(game_slug='valorant', page=2, per_page=12)

        request = mock_urlopen.call_args.args[0]
        self.assertIn('/valorant/players', request.full_url)
        self.assertIn('page%5Bnumber%5D=2', request.full_url)
        self.assertEqual(request.headers['Authorization'], 'Bearer test-token')

    @patch('apps.games.services.pandascore._read_dotenv_value', return_value='')
    @patch.dict('os.environ', {}, clear=True)
    def test_requires_server_side_token(self, mock_read_dotenv_value):
        with self.assertRaises(PandaScoreConfigError):
            PandaScoreClient()


class PlayersListViewTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name='Valorant', slug='valorant')
        self.team = Team.objects.create(game=self.game, name='Sentinels', slug='sentinels')
        self.player = Player.objects.create(
            game=self.game,
            team=self.team,
            ign='zekken',
            real_name='Zachary Patrone',
            country='United States',
            role='Duelist',
        )

    @patch('apps.games.services.pandascore._read_dotenv_value', return_value='')
    @patch.dict('os.environ', {}, clear=True)
    def test_players_page_falls_back_to_local_data_without_token(self, mock_read_dotenv_value):
        response = self.client.get(reverse('players_list', kwargs={'slug': self.game.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'zekken')
        self.assertContains(response, 'PANDASCORE_API_TOKEN')
