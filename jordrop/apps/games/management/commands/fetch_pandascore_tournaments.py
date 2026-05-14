from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.games.models import Game
from apps.games.services import PandaScoreAPIError, PandaScoreClient, PandaScoreConfigError
from apps.tournaments.models import Tournament


STATUS_MAP = {
    'not_started': Tournament.STATUS_UPCOMING,
    'not started': Tournament.STATUS_UPCOMING,
    'running': Tournament.STATUS_ONGOING,
    'finished': Tournament.STATUS_FINISHED,
    'canceled': Tournament.STATUS_FINISHED,
    'cancelled': Tournament.STATUS_FINISHED,
}


class Command(BaseCommand):
    help = 'Fetch tournaments from PandaScore for a game and optionally save them locally.'

    def add_arguments(self, parser):
        parser.add_argument('game_slug', help='Local game slug, for example valorant or counter-strike-2.')
        parser.add_argument('--search', default='', help='Search tournaments by PandaScore name.')
        parser.add_argument('--page', type=int, default=1)
        parser.add_argument('--per-page', type=int, default=10)
        parser.add_argument('--save', action='store_true', help='Save fetched tournaments locally.')

    def handle(self, *args, **options):
        game = self._get_game(options['game_slug'])

        try:
            tournaments = PandaScoreClient().list_tournaments(
                game_slug=game.slug,
                page=options['page'],
                per_page=options['per_page'],
                search=options['search'],
            )
        except PandaScoreConfigError as exc:
            raise CommandError(str(exc)) from exc
        except PandaScoreAPIError as exc:
            raise CommandError(str(exc)) from exc

        if not tournaments:
            self.stdout.write(self.style.WARNING('No PandaScore tournaments found.'))
            return

        saved_count = 0
        for tournament_data in tournaments:
            tournament = self._normalize_tournament(tournament_data)
            self.stdout.write(
                self._safe_console_text(
                    f"{tournament['name']} | {tournament['status']} | "
                    f"{tournament['start_date'] or 'TBD'} - {tournament['end_date'] or 'TBD'}"
                )
            )

            if options['save']:
                self._save_tournament(game, tournament)
                saved_count += 1

        self.stdout.write(self.style.SUCCESS(f'Fetched {len(tournaments)} tournament(s) from PandaScore.'))
        if options['save']:
            self.stdout.write(self.style.SUCCESS(f'Saved {saved_count} tournament(s) locally.'))

    def _get_game(self, game_slug):
        try:
            return Game.objects.get(slug=game_slug)
        except Game.DoesNotExist as exc:
            raise CommandError(f'Game not found: {game_slug}. Run seed_esports_games first or create it in admin.') from exc

    def _normalize_tournament(self, tournament_data):
        serie = tournament_data.get('serie') or {}
        league = tournament_data.get('league') or {}
        name = tournament_data.get('name') or tournament_data.get('slug') or 'Unnamed tournament'

        return {
            'pandascore_id': tournament_data.get('id'),
            'name': name,
            'slug': tournament_data.get('slug') or slugify(name),
            'status': STATUS_MAP.get((tournament_data.get('status') or '').lower(), Tournament.STATUS_UPCOMING),
            'start_date': self._parse_date(tournament_data.get('begin_at')),
            'end_date': self._parse_date(tournament_data.get('end_at')),
            'prize_pool': tournament_data.get('prizepool') or '',
            'description': self._build_description(league, serie),
        }

    def _save_tournament(self, game, tournament):
        lookup = {'game': game}
        if tournament['pandascore_id']:
            lookup['pandascore_id'] = tournament['pandascore_id']
        else:
            lookup['slug'] = tournament['slug']

        Tournament.objects.update_or_create(
            **lookup,
            defaults={
                'slug': tournament['slug'],
                'pandascore_id': tournament['pandascore_id'],
                'name': tournament['name'],
                'format': Tournament.FORMAT_SINGLE_ELIM,
                'status': tournament['status'],
                'prize_pool': tournament['prize_pool'],
                'start_date': tournament['start_date'],
                'end_date': tournament['end_date'],
                'description': tournament['description'],
            },
        )

    def _parse_date(self, value):
        if not value:
            return None

        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        except ValueError:
            return None

    def _build_description(self, league, serie):
        parts = []
        if league.get('name'):
            parts.append(f"League: {league['name']}")
        if serie.get('full_name') or serie.get('name'):
            parts.append(f"Series: {serie.get('full_name') or serie.get('name')}")
        return ' | '.join(parts)

    def _safe_console_text(self, value):
        return value.encode('ascii', errors='replace').decode('ascii')
