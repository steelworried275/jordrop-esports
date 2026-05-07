from django.contrib import admin
from .models import Game, Team, Player


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'accent_color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'country']
    list_filter = ['game']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['ign', 'real_name', 'team', 'game', 'role']
    list_filter = ['game']
    search_fields = ['ign', 'real_name']
