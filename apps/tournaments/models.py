from django.db import models
from apps.games.models import Game, Team

class Tournament(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('finished', 'Finished'),
    ]
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='tournaments')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    prize_pool = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start_date']


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team_a = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_matches')
    team_b = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='away_matches')
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    played_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    round_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} — {self.tournament}"
