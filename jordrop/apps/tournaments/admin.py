from django.contrib import admin
from .models import Match, Tournament
from .services import generate_single_elimination
from apps.games.models import Team


class MatchInline(admin.TabularInline):
    model = Match
    extra = 1
    fields = ['round_number', 'match_number', 'round_label', 'team_a', 'team_b',
              'score_a', 'score_b', 'winner', 'is_finished', 'played_at']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'format', 'status', 'prize_pool', 'start_date']
    list_filter = ['game', 'status', 'format']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MatchInline]
    actions = ['generate_bracket']

    @admin.action(description='Generate single-elimination bracket from game teams')
    def generate_bracket(self, request, queryset):
        for tournament in queryset:
            teams = list(Team.objects.filter(game=tournament.game))
            if len(teams) >= 2:
                generate_single_elimination(tournament, teams)
                self.message_user(request, f'Bracket generated for {tournament.name}.')
            else:
                self.message_user(request, f'{tournament.name}: need at least 2 teams.', level='warning')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'round_number', 'score_a', 'score_b', 'winner', 'is_finished']
    list_filter = ['tournament', 'is_finished']
