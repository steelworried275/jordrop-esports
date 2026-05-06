from django.urls import path
from . import views

urlpatterns = [
    path('<slug:game_slug>/', views.wiki_list, name='wiki_list'),
    path('<slug:game_slug>/<slug:slug>/', views.wiki_detail, name='wiki_detail'),
]
