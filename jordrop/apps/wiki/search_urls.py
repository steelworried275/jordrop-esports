from django.urls import path
from .search_views import search

urlpatterns = [
    path('', search, name='search'),
]
