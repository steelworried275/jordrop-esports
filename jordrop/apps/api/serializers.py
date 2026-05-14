from rest_framework import serializers
from apps.games.models import Game, Team, Player
from apps.wiki.models import Page, PageRevision, EditRequest
from apps.tournaments.models import Tournament, Match


# ── Games ─────────────────────────────────────────────────────────────────────

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'slug', 'accent_color', 'image_url', 'description', 'created_at']


class TeamSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source='game.name', read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'slug', 'game', 'game_name', 'country', 'founded', 'bio',
                  'pandascore_id', 'image_url']


class PlayerSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source='game.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True, default=None)

    class Meta:
        model = Player
        fields = ['id', 'ign', 'real_name', 'game', 'game_name', 'team', 'team_name',
                  'country', 'role', 'pandascore_id', 'image_url']


# ── Wiki ──────────────────────────────────────────────────────────────────────

class PageRevisionSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = PageRevision
        fields = ['id', 'revision_number', 'content', 'content_rendered',
                  'edit_summary', 'author_username', 'created_at']
        read_only_fields = ['revision_number', 'content_rendered', 'created_at']


class PageSerializer(serializers.ModelSerializer):
    game_slug = serializers.CharField(source='game.slug', read_only=True)
    current_revision = PageRevisionSerializer(read_only=True)

    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'game', 'game_slug', 'is_published',
                  'current_revision', 'created_at', 'updated_at']


class EditRequestSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    page_title = serializers.CharField(source='page.title', read_only=True)

    class Meta:
        model = EditRequest
        fields = ['id', 'page', 'page_title', 'proposed_content', 'edit_summary',
                  'status', 'author_username', 'review_comment', 'created_at']
        read_only_fields = ['status', 'review_comment', 'created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


# ── Tournaments ───────────────────────────────────────────────────────────────

class MatchSerializer(serializers.ModelSerializer):
    team_a_name = serializers.CharField(source='team_a.name', read_only=True, default=None)
    team_b_name = serializers.CharField(source='team_b.name', read_only=True, default=None)
    winner_name = serializers.CharField(source='winner.name', read_only=True, default=None)

    class Meta:
        model = Match
        fields = ['id', 'round_number', 'match_number', 'round_label',
                  'team_a', 'team_a_name', 'team_b', 'team_b_name',
                  'score_a', 'score_b', 'winner', 'winner_name',
                  'is_finished', 'played_at']


class TournamentSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source='game.name', read_only=True)
    matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'slug', 'game', 'game_name', 'format',
                  'status', 'prize_pool', 'location', 'start_date', 'end_date',
                  'description', 'pandascore_id', 'matches']
