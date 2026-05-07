from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('games', views.GameViewSet)
router.register('teams', views.TeamViewSet)
router.register('players', views.PlayerViewSet)
router.register('pages', views.PageViewSet)
router.register('revisions', views.PageRevisionViewSet)
router.register('edit-requests', views.EditRequestViewSet)
router.register('tournaments', views.TournamentViewSet)

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
