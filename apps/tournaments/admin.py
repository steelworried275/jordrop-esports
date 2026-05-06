from django.contrib import admin
from .models import Tournament, Match

class MatchInline(admin.TabularInline):
    model = Match
    extra = 1
    fields = ['team_a', 'team_b', 'score_a', 'score_b', 'round_name', 'played_at', 'is_finished']

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'status', 'prize_pool', 'start_date', 'end_date']
    list_filter = ['game', 'status']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MatchInline]

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'score_a', 'score_b', 'round_name', 'is_finished']
    list_filter = ['tournament', 'is_finished']
