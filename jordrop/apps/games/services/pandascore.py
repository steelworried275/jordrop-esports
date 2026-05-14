import json
import os
from pathlib import Path
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PandaScoreConfigError(RuntimeError):
    pass


class PandaScoreAPIError(RuntimeError):
    pass


GAME_ENDPOINTS = {
    'call-of-duty': 'codmw',
    'cod': 'codmw',
    'counter-strike': 'csgo',
    'counter-strike-2': 'csgo',
    'cs2': 'csgo',
    'csgo': 'csgo',
    'dota-2': 'dota2',
    'dota2': 'dota2',
    'league-of-legends': 'lol',
    'lol': 'lol',
    'mobile-legends': 'mlbb',
    'mobile-legends-bang-bang': 'mlbb',
    'mlbb': 'mlbb',
    'overwatch': 'ow',
    'rainbow-six-siege': 'r6siege',
    'r6siege': 'r6siege',
    'rocket-league': 'rl',
    'starcraft-2': 'starcraft-2',
    'valorant': 'valorant',
}


class PandaScoreClient:
    def __init__(self, token=None, base_url=None, timeout=None):
        self.token = token or os.environ.get('PANDASCORE_API_TOKEN') or _read_dotenv_value('PANDASCORE_API_TOKEN')
        self.base_url = (base_url or os.environ.get('PANDASCORE_API_BASE_URL') or 'https://api.pandascore.co').rstrip('/')
        self.timeout = int(timeout or os.environ.get('PANDASCORE_TIMEOUT', 10))

        if not self.token:
            raise PandaScoreConfigError('PANDASCORE_API_TOKEN is not configured.')

    def list_players(self, game_slug='', page=1, per_page=24, search=''):
        return self._list_resource('players', game_slug=game_slug, page=page, per_page=per_page, search=search)

    def list_teams(self, game_slug='', page=1, per_page=24, search=''):
        return self._list_resource('teams', game_slug=game_slug, page=page, per_page=per_page, search=search)

    def list_tournaments(self, game_slug='', page=1, per_page=24, search=''):
        return self._list_resource('tournaments', game_slug=game_slug, page=page, per_page=per_page, search=search)

    def list_matches(self, game_slug='', page=1, per_page=24, search=''):
        return self._list_resource('matches', game_slug=game_slug, page=page, per_page=per_page, search=search)

    def list_videogames(self, page=1, per_page=100, search=''):
        params = {
            'page[number]': max(int(page or 1), 1),
            'page[size]': min(max(int(per_page or 100), 1), 100),
        }
        if search:
            params['search[name]'] = search
        return self._get('/videogames', params=params)

    def _list_resource(self, resource, game_slug='', page=1, per_page=24, search=''):
        params = {
            'page[number]': max(int(page or 1), 1),
            'page[size]': min(max(int(per_page or 24), 1), 100),
        }
        if search:
            params['search[name]'] = search

        game_endpoint = GAME_ENDPOINTS.get(_normalize_slug(game_slug))
        endpoint = f'/{game_endpoint}/{resource}' if game_endpoint else f'/{resource}'
        return self._get(endpoint, params=params)

    def _get(self, endpoint, params=None):
        query = f'?{urlencode(params)}' if params else ''
        request = Request(
            f'{self.base_url}{endpoint}{query}',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}',
            },
            method='GET',
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            raise PandaScoreAPIError(f'PandaScore returned HTTP {exc.code}.') from exc
        except (URLError, SocketTimeout, TimeoutError) as exc:
            raise PandaScoreAPIError('PandaScore is currently unreachable.') from exc
        except json.JSONDecodeError as exc:
            raise PandaScoreAPIError('PandaScore returned an invalid JSON response.') from exc


def _normalize_slug(value):
    return (value or '').strip().lower().replace('_', '-').replace(' ', '-')


def _read_dotenv_value(key):
    for env_path in _candidate_env_paths():
        if not env_path.exists():
            continue

        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            name, value = line.split('=', 1)
            if name.strip() == key:
                return value.strip().strip('"').strip("'")

    return ''


def _candidate_env_paths():
    cwd = Path.cwd()
    service_dir = Path(__file__).resolve()
    return [
        cwd / '.env',
        cwd.parent / '.env',
        service_dir.parents[3] / '.env',
    ]
