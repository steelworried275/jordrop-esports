from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('game/<slug:slug>/', views.game_detail, name='game_detail'),
    path('game/<slug:slug>/teams/', views.teams_list, name='teams_list'),
    path('game/<slug:slug>/players/', views.players_list, name='players_list'),
]
