from django.urls import path
from . import views

urlpatterns = [
    path('', views.tournaments_home, name='tournaments_home'),
    path('<int:pk>/', views.tournament_detail, name='tournament_detail'),
]
