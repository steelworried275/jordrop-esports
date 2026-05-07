from django.shortcuts import render, get_object_or_404
from .models import Game, Team, Player
from apps.tournaments.models import Tournament


def home(request):
    games = Game.objects.all()
    recent_tournaments = Tournament.objects.filter(status__in=['ongoing', 'upcoming'])[:5]
    return render(request, 'games/home.html', {'games': games, 'recent_tournaments': recent_tournaments})


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


def players_list(request, slug):
    game = get_object_or_404(Game, slug=slug)
    players = game.players.select_related('team').all()
    return render(request, 'games/players.html', {'game': game, 'players': players})
