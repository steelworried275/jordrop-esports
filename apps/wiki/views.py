from django.shortcuts import render, get_object_or_404
from .models import Article
from apps.games.models import Game

def wiki_list(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    articles = game.articles.filter(is_published=True)
    return render(request, 'wiki/list.html', {'game': game, 'articles': articles})

def wiki_detail(request, game_slug, slug):
    game = get_object_or_404(Game, slug=game_slug)
    article = get_object_or_404(Article, game=game, slug=slug, is_published=True)
    return render(request, 'wiki/detail.html', {'game': game, 'article': article})
