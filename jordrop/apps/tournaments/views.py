from django.shortcuts import render, get_object_or_404
from .models import Tournament, Match
from apps.games.models import Game


def tournaments_home(request):
    game_slug = request.GET.get('game')
    games = Game.objects.all()
    tournaments = Tournament.objects.select_related('game').all()
    if game_slug:
        tournaments = tournaments.filter(game__slug=game_slug)
    return render(request, 'tournaments/list.html', {
        'tournaments': tournaments, 'games': games, 'selected': game_slug,
    })


def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    # Group matches by round_number for bracket display
    matches = (
        tournament.matches
        .select_related('team_a', 'team_b', 'winner', 'next_match')
        .order_by('round_number', 'match_number')
    )
    rounds = {}
    for match in matches:
        rounds.setdefault(match.round_number, {
            'label': match.round_label or f'Round {match.round_number}',
            'matches': [],
        })['matches'].append(match)

    return render(request, 'tournaments/detail.html', {
        'tournament': tournament,
        'rounds': dict(sorted(rounds.items())),
    })
