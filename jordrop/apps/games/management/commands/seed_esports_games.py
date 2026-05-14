from django.core.management.base import BaseCommand

from apps.games.models import Game


DEFAULT_GAMES = [
    {
        'name': 'League of Legends',
        'slug': 'league-of-legends',
        'accent_color': '#0AC8B9',
        'description': 'MOBA esports coverage for teams, players, tournaments, matches, and wiki pages.',
    },
    {
        'name': 'VALORANT',
        'slug': 'valorant',
        'accent_color': '#FF4655',
        'description': 'Tactical shooter esports coverage for rosters, events, matches, and competitive history.',
    },
    {
        'name': 'Counter-Strike 2',
        'slug': 'counter-strike-2',
        'accent_color': '#F7B500',
        'description': 'Counter-Strike esports coverage using the PandaScore CS:GO/CS2 data namespace.',
    },
    {
        'name': 'Dota 2',
        'slug': 'dota-2',
        'accent_color': '#D44832',
        'description': 'Dota 2 esports coverage for teams, players, tournaments, and matches.',
    },
    {
        'name': 'Rocket League',
        'slug': 'rocket-league',
        'accent_color': '#2D9CDB',
        'description': 'Rocket League esports coverage for teams, players, tournament brackets, and results.',
    },
    {
        'name': 'Rainbow Six Siege',
        'slug': 'rainbow-six-siege',
        'accent_color': '#00A3FF',
        'description': 'Rainbow Six Siege esports coverage for pro teams, players, and international events.',
    },
]


class Command(BaseCommand):
    help = 'Seed the core esports game pages used by the wiki.'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for game_data in DEFAULT_GAMES:
            _, created = Game.objects.update_or_create(
                slug=game_data['slug'],
                defaults=game_data,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded games: {created_count} created, {updated_count} updated.'
            )
        )
