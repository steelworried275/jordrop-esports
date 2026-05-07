from apps.games.models import Game

def nav_games(request):
    try:
        games = Game.objects.all()
    except Exception:
        games = []
    return {'nav_games': games}
