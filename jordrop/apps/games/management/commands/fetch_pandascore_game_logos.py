from django.core.management.base import BaseCommand, CommandError

from apps.games.models import Game
from apps.games.services import PandaScoreAPIError, PandaScoreClient, PandaScoreConfigError


PANDASCORE_TO_LOCAL_SLUGS = {
    'csgo': 'counter-strike-2',
    'counter-strike': 'counter-strike-2',
    'counter-strike-2': 'counter-strike-2',
    'dota2': 'dota-2',
    'dota-2': 'dota-2',
    'lol': 'league-of-legends',
    'league-of-legends': 'league-of-legends',
    'r6siege': 'rainbow-six-siege',
    'rainbow-six-siege': 'rainbow-six-siege',
    'rl': 'rocket-league',
    'rocket-league': 'rocket-league',
    'valorant': 'valorant',
}

INTERNET_LOGO_URLS = {
    'counter-strike-2': 'https://commons.wikimedia.org/wiki/Special:FilePath/Counter-Strike_2_logo.svg',
    'dota-2': 'https://commons.wikimedia.org/wiki/Special:FilePath/Dota-2-simplified-logo.svg',
    'league-of-legends': 'https://commons.wikimedia.org/wiki/Special:FilePath/League_of_legends_logo.png',
    'rainbow-six-siege': 'https://commons.wikimedia.org/wiki/Special:FilePath/Rainbow_Six_Siege_X_logo.svg',
    'rocket-league': 'https://commons.wikimedia.org/wiki/Special:FilePath/Rocket_League_logo.svg',
    'valorant': 'https://commons.wikimedia.org/wiki/Special:FilePath/Valorant_logo.svg',
}


class Command(BaseCommand):
    help = 'Fetch game logo URLs from PandaScore, then fill missing logos from public internet sources.'

    def handle(self, *args, **options):
        try:
            videogames = PandaScoreClient().list_videogames(per_page=100)
        except PandaScoreConfigError as exc:
            raise CommandError(str(exc)) from exc
        except PandaScoreAPIError as exc:
            raise CommandError(str(exc)) from exc

        pandascore_updated_count = 0
        skipped_count = 0

        for videogame in videogames:
            local_slug = self._local_slug_for(videogame)
            image_url = videogame.get('image_url') or ''
            if not local_slug or not image_url:
                skipped_count += 1
                continue

            updated = Game.objects.filter(slug=local_slug).update(image_url=image_url)
            if updated:
                pandascore_updated_count += updated
                self.stdout.write(f"{local_slug} <- {image_url}")
            else:
                skipped_count += 1

        internet_updated_count = self._fill_missing_from_internet()
        self.stdout.write(self.style.SUCCESS(
            f'Updated {pandascore_updated_count} from PandaScore, '
            f'{internet_updated_count} from internet fallback. Skipped {skipped_count}.'
        ))

    def _local_slug_for(self, videogame):
        slug = (videogame.get('slug') or '').strip().lower()
        name = (videogame.get('name') or '').strip().lower().replace(' ', '-')
        return PANDASCORE_TO_LOCAL_SLUGS.get(slug) or PANDASCORE_TO_LOCAL_SLUGS.get(name)

    def _fill_missing_from_internet(self):
        updated_count = 0
        for slug, image_url in INTERNET_LOGO_URLS.items():
            updated = Game.objects.filter(slug=slug, image_url='').update(image_url=image_url)
            if updated:
                updated_count += updated
                self.stdout.write(f"{slug} <- {image_url}")
        return updated_count
