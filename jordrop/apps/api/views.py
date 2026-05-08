import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.games.models import Game, Team, Player
from apps.wiki.models import Page, PageRevision, EditRequest
from apps.tournaments.models import Tournament, Match
from .serializers import (
    GameSerializer, TeamSerializer, PlayerSerializer,
    PageSerializer, PageRevisionSerializer, EditRequestSerializer,
    TournamentSerializer, MatchSerializer,
)
from .permissions import IsModeratorOrAdmin, IsContributorOrReadOnly


class GroqChatThrottle(AnonRateThrottle):
    rate = '30/hour'


class GroqChatView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [GroqChatThrottle]

    def post(self, request):
        message = str(request.data.get('message', '')).strip()
        if not message:
            return Response({'detail': 'Message is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(message) > 4000:
            return Response(
                {'detail': 'Message is too long. Please keep it under 4000 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not settings.GROQ_API_KEY:
            return Response(
                {'detail': 'Groq is not configured. Set GROQ_API_KEY on the server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        payload = {
            'model': settings.GROQ_MODEL,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'You are the JORDROP esports assistant. Answer questions about '
                        'esports, tournaments, teams, players, and wiki editing in a '
                        'concise, practical way. If you do not know, say so.'
                    ),
                },
                {'role': 'user', 'content': message},
            ],
            'temperature': 0.4,
            'max_completion_tokens': 700,
        }

        groq_request = Request(
            settings.GROQ_CHAT_COMPLETIONS_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'JORDROP-Esports/1.0',
            },
            method='POST',
        )

        try:
            with urlopen(groq_request, timeout=settings.GROQ_REQUEST_TIMEOUT) as response:
                result = json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            detail = self._read_error_detail(exc)
            return Response({'detail': detail}, status=exc.code)
        except (URLError, TimeoutError, json.JSONDecodeError):
            return Response(
                {'detail': 'Groq request failed. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        answer = (
            result.get('choices', [{}])[0]
            .get('message', {})
            .get('content', '')
            .strip()
        )
        if not answer:
            return Response(
                {'detail': 'Groq returned an empty response.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({'answer': answer, 'model': settings.GROQ_MODEL})

    def _read_error_detail(self, exc):
        try:
            body = json.loads(exc.read().decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return 'Groq returned an error.'
        return body.get('error', {}).get('message') or body.get('detail') or 'Groq returned an error.'


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
