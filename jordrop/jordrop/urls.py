from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.games.urls')),
    path('wiki/', include('apps.wiki.urls')),
    path('tournaments/', include('apps.tournaments.urls')),
    path('accounts/', include('apps.users.urls')),
    path('search/', include('apps.wiki.search_urls')),
    path('api/', include('apps.api.urls')),
    path('markdownx/', include('markdownx.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
