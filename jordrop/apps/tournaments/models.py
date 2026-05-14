from django.db import models
from apps.core.models import TimeStampedModel
from apps.games.models import Game, Team


class Tournament(TimeStampedModel):
    STATUS_UPCOMING = 'upcoming'
    STATUS_ONGOING = 'ongoing'
    STATUS_FINISHED = 'finished'
    STATUS_CHOICES = [
        (STATUS_UPCOMING, 'Upcoming'),
        (STATUS_ONGOING, 'Ongoing'),
        (STATUS_FINISHED, 'Finished'),
    ]

    FORMAT_SINGLE_ELIM = 'single_elimination'
    FORMAT_DOUBLE_ELIM = 'double_elimination'
    FORMAT_ROUND_ROBIN = 'round_robin'
    FORMAT_CHOICES = [
        (FORMAT_SINGLE_ELIM, 'Single Elimination'),
        (FORMAT_DOUBLE_ELIM, 'Double Elimination'),
        (FORMAT_ROUND_ROBIN, 'Round Robin'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='tournaments')
    pandascore_id = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    format = models.CharField(max_length=25, choices=FORMAT_CHOICES, default=FORMAT_SINGLE_ELIM)
    prize_pool = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start_date']


class Match(TimeStampedModel):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')

    # Structured round tracking (replaces free-text round_name)
    round_number = models.PositiveSmallIntegerField(
        help_text='1=Quarter-final, 2=Semi-final, 3=Final, etc.'
    )
    match_number = models.PositiveSmallIntegerField(
        help_text='Position within the round (1-indexed).'
    )
    round_label = models.CharField(max_length=50, blank=True, help_text='Display label e.g. "Quarter-final"')

    team_a = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_matches')
    team_b = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='away_matches')
    score_a = models.PositiveSmallIntegerField(default=0)
    score_b = models.PositiveSmallIntegerField(default=0)
    winner = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches'
    )

    # Self-reference: winner of this match feeds into next_match
    next_match = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='feeder_matches'
    )

    played_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['round_number', 'match_number']
        unique_together = ('tournament', 'round_number', 'match_number')

    def __str__(self):
        a = self.team_a.name if self.team_a else 'TBD'
        b = self.team_b.name if self.team_b else 'TBD'
        return f'{a} vs {b} — {self.tournament.name} R{self.round_number}M{self.match_number}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically slot winner into the next match after save
        if self.is_finished and self.winner and self.next_match:
            nxt = self.next_match
            changed = False
            if nxt.team_a is None:
                nxt.team_a = self.winner
                changed = True
            elif nxt.team_b is None and nxt.team_a != self.winner:
                nxt.team_b = self.winner
                changed = True
            if changed:
                nxt.save(update_fields=['team_a', 'team_b', 'updated_at'])
