from django.db.models import Q
from django.shortcuts import render

from apps.games.models import Player, Team
from .models import Page


def search(request):
    q = request.GET.get('q', '').strip()
    pages, teams, players = [], [], []

    if q:
        # Wiki pages: search title and current revision content
        pages = (
            Page.objects.filter(is_published=True)
            .filter(
                Q(title__icontains=q) |
                Q(current_revision__content__icontains=q)
            )
            .select_related('game', 'current_revision')
            .distinct()[:20]
        )

        teams = Team.objects.filter(name__icontains=q).select_related('game')[:10]

        players = Player.objects.filter(
            Q(ign__icontains=q) | Q(real_name__icontains=q)
        ).select_related('team', 'game')[:10]

    return render(request, 'search/results.html', {
        'q': q,
        'pages': pages,
        'teams': teams,
        'players': players,
    })
