from django.shortcuts import render, get_object_or_404
from .models import Tournament
from apps.games.models import Game

def tournaments_home(request):
    game_slug = request.GET.get('game')
    games = Game.objects.all()
    tournaments = Tournament.objects.select_related('game').all()
    if game_slug:
        tournaments = tournaments.filter(game__slug=game_slug)
    return render(request, 'tournaments/list.html', {
        'tournaments': tournaments, 'games': games, 'selected': game_slug
    })

def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = tournament.matches.select_related('team_a', 'team_b').all()
    return render(request, 'tournaments/detail.html', {
        'tournament': tournament, 'matches': matches
    })
