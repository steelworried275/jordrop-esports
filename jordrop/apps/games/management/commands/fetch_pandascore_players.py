from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.games.models import Game, Player, Team
from apps.games.services import PandaScoreAPIError, PandaScoreClient, PandaScoreConfigError


class Command(BaseCommand):
    help = 'Fetch players from PandaScore for a game, with optional local import.'

    def add_arguments(self, parser):
        parser.add_argument('game_slug', help='Local game slug, for example valorant or league-of-legends.')
        parser.add_argument('--search', default='', help='Search players by PandaScore name.')
        parser.add_argument('--page', type=int, default=1)
        parser.add_argument('--per-page', type=int, default=10)
        parser.add_argument('--save', action='store_true', help='Save fetched players and current teams locally.')

    def handle(self, *args, **options):
        game = self._get_game(options['game_slug'])

        try:
            players = PandaScoreClient().list_players(
                game_slug=game.slug,
                page=options['page'],
                per_page=options['per_page'],
                search=options['search'],
            )
        except PandaScoreConfigError as exc:
            raise CommandError(str(exc)) from exc
        except PandaScoreAPIError as exc:
            raise CommandError(str(exc)) from exc

        if not players:
            self.stdout.write(self.style.WARNING('No PandaScore players found.'))
            return

        saved_count = 0
        for player_data in players:
            player = self._normalize_player(player_data)
            self.stdout.write(
                self._safe_console_text(
                    f"{player['handle']} | {player['real_name'] or 'Unknown name'} | "
                    f"{player['team_name'] or 'Free agent'} | {player['country'] or 'Unknown country'}"
                )
            )

            if options['save']:
                self._save_player(game, player)
                saved_count += 1

        self.stdout.write(self.style.SUCCESS(f'Fetched {len(players)} player(s) from PandaScore.'))
        if options['save']:
            self.stdout.write(self.style.SUCCESS(f'Saved {saved_count} player(s) locally.'))

    def _get_game(self, game_slug):
        try:
            return Game.objects.get(slug=game_slug)
        except Game.DoesNotExist as exc:
            raise CommandError(f'Game not found: {game_slug}. Run seed_esports_games first or create it in admin.') from exc

    def _normalize_player(self, player_data):
        first_name = player_data.get('first_name') or ''
        last_name = player_data.get('last_name') or ''
        team = player_data.get('current_team') or player_data.get('team') or {}

        return {
            'pandascore_id': player_data.get('id'),
            'handle': player_data.get('name') or player_data.get('slug') or 'Unknown player',
            'real_name': f'{first_name} {last_name}'.strip(),
            'team_name': team.get('name') or '',
            'team_slug': team.get('slug') or '',
            'team_pandascore_id': team.get('id'),
            'team_image_url': team.get('image_url') or '',
            'country': player_data.get('nationality') or player_data.get('hometown') or '',
            'role': player_data.get('role') or '',
            'image_url': player_data.get('image_url') or '',
        }

    def _save_player(self, game, player):
        team = None
        if player['team_name']:
            team_slug = player['team_slug'] or slugify(player['team_name'])
            team, _ = Team.objects.update_or_create(
                game=game,
                slug=team_slug,
                defaults={
                    'name': player['team_name'],
                    'pandascore_id': player['team_pandascore_id'],
                    'image_url': player['team_image_url'],
                },
            )

        Player.objects.update_or_create(
            game=game,
            ign=player['handle'],
            defaults={
                'pandascore_id': player['pandascore_id'],
                'real_name': player['real_name'],
                'team': team,
                'country': player['country'],
                'role': player['role'],
                'image_url': player['image_url'],
            },
        )

    def _safe_console_text(self, value):
        return value.encode('ascii', errors='replace').decode('ascii')
