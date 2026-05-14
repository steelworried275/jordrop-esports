from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Game, Team, Player
from apps.tournaments.models import Tournament
from apps.wiki.models import EditRequest
from .services import PandaScoreAPIError, PandaScoreClient, PandaScoreConfigError


def home(request):
    games = Game.objects.all()
    recent_tournaments = Tournament.objects.filter(status__in=['ongoing', 'upcoming'])[:5]
    pending_submissions = EditRequest.objects.none()
    if request.user.is_authenticated and request.user.is_contributor:
        pending_submissions = (
            EditRequest.objects
            .filter(author=request.user, status=EditRequest.STATUS_PENDING)
            .select_related('page', 'page__game')
            .order_by('-created_at')[:8]
        )
    return render(request, 'games/home.html', {
        'games': games,
        'recent_tournaments': recent_tournaments,
        'pending_submissions': pending_submissions,
    })


def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    teams = game.teams.all()[:8]
    tournaments = game.tournaments.all()[:5]
    return render(request, 'games/game_detail.html', {
        'game': game, 'teams': teams, 'tournaments': tournaments,
    })


def teams_list(request, slug):
    game = get_object_or_404(Game, slug=slug)
    teams = game.teams.prefetch_related('players').all()
    return render(request, 'games/teams.html', {'game': game, 'teams': teams})


def team_detail(request, game_slug, team_slug):
    game = get_object_or_404(Game, slug=game_slug)
    team = get_object_or_404(
        Team.objects.select_related('game').prefetch_related('players'),
        game=game,
        slug=team_slug,
    )
    players = team.players.select_related('game').all()
    return render(request, 'games/team_detail.html', {
        'game': game,
        'team': team,
        'players': players,
    })


def players_list(request, slug):
    game = get_object_or_404(Game, slug=slug)
    query = request.GET.get('q', '').strip()
    page = _positive_int(request.GET.get('page'), default=1)
    local_players = _local_players(game, query)
    players = [_serialize_local_player(player) for player in local_players]
    source_label = 'Local wiki database'
    api_error = ''
    api_notice = ''
    has_next_page = False

    try:
        live_players = PandaScoreClient().list_players(
            game_slug=game.slug,
            page=page,
            per_page=24,
            search=query,
        )
        players = [_serialize_pandascore_player(player) for player in live_players]
        source_label = 'PandaScore live API'
        has_next_page = len(players) == 24
    except PandaScoreConfigError:
        api_notice = 'Live PandaScore data is disabled because PANDASCORE_API_TOKEN is not configured.'
    except PandaScoreAPIError as exc:
        api_error = str(exc)

    return render(request, 'games/players.html', {
        'game': game,
        'players': players,
        'query': query,
        'page_number': page,
        'previous_page': page - 1,
        'next_page': page + 1,
        'has_previous_page': page > 1,
        'has_next_page': has_next_page,
        'source_label': source_label,
        'api_error': api_error,
        'api_notice': api_notice,
        'local_players_count': local_players.count(),
    })


def _local_players(game, query=''):
    players = game.players.select_related('team').all()
    if query:
        players = players.filter(
            Q(ign__icontains=query)
            | Q(real_name__icontains=query)
            | Q(team__name__icontains=query)
            | Q(country__icontains=query)
            | Q(role__icontains=query)
        )
    return players


def _serialize_local_player(player):
    return {
        'id': player.pk,
        'handle': player.ign,
        'real_name': player.real_name,
        'team_name': player.team.name if player.team else '',
        'role': player.role,
        'country': player.country,
        'image_url': player.photo.url if player.photo else player.image_url,
        'source': 'Local',
    }


def _serialize_pandascore_player(player):
    first_name = player.get('first_name') or ''
    last_name = player.get('last_name') or ''
    team = player.get('current_team') or player.get('team') or {}
    videogame = player.get('current_videogame') or player.get('videogame') or {}

    return {
        'id': player.get('id'),
        'handle': player.get('name') or player.get('slug') or 'Unknown player',
        'real_name': f'{first_name} {last_name}'.strip(),
        'team_name': team.get('name') or '',
        'role': player.get('role') or '',
        'country': player.get('nationality') or player.get('hometown') or '',
        'image_url': player.get('image_url') or '',
        'game_name': videogame.get('name') or '',
        'source': 'PandaScore',
    }


def _positive_int(value, default=1):
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return default
