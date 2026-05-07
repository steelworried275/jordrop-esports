from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.games.models import Game, Team, Player
from apps.wiki.models import Page, PageRevision, EditRequest
from apps.tournaments.models import Tournament, Match
from .serializers import (
    GameSerializer, TeamSerializer, PlayerSerializer,
    PageSerializer, PageRevisionSerializer, EditRequestSerializer,
    TournamentSerializer, MatchSerializer,
)
from .permissions import IsModeratorOrAdmin, IsContributorOrReadOnly


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'slug'


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.select_related('game').all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        game_slug = self.request.query_params.get('game')
        if game_slug:
            qs = qs.filter(game__slug=game_slug)
        return qs


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.select_related('game', 'team').all()
    serializer_class = PlayerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        game_slug = self.request.query_params.get('game')
        if game_slug:
            qs = qs.filter(game__slug=game_slug)
        return qs


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.filter(is_published=True).select_related('game', 'current_revision')
    serializer_class = PageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        game_slug = self.request.query_params.get('game')
        if game_slug:
            qs = qs.filter(game__slug=game_slug)
        return qs


class PageRevisionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageRevision.objects.select_related('page', 'author').all()
    serializer_class = PageRevisionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        page_id = self.request.query_params.get('page')
        if page_id:
            qs = qs.filter(page_id=page_id)
        return qs


class EditRequestViewSet(viewsets.ModelViewSet):
    queryset = EditRequest.objects.select_related('page', 'author', 'reviewed_by').all()
    serializer_class = EditRequestSerializer
    permission_classes = [IsContributorOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        # Non-moderators can only see their own edit requests
        user = self.request.user
        if user.is_authenticated and not user.is_moderator:
            qs = qs.filter(author=user)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def approve(self, request, pk=None):
        edit = self.get_object()
        if edit.status != EditRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending edits can be approved.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        revision = edit.approve(request.user)
        return Response({'status': 'approved', 'revision_id': revision.pk})

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def reject(self, request, pk=None):
        edit = self.get_object()
        if edit.status != EditRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending edits can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        edit.reject(request.user, comment=request.data.get('comment', ''))
        return Response({'status': 'rejected'})


class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tournament.objects.select_related('game').prefetch_related('matches')
    serializer_class = TournamentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        game_slug = self.request.query_params.get('game')
        if game_slug:
            qs = qs.filter(game__slug=game_slug)
        return qs
