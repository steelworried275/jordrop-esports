from django.db import models
from apps.core.models import TimeStampedModel


class Game(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    accent_color = models.CharField(max_length=7, default='#00e5ff')
    logo = models.ImageField(upload_to='games/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Team(TimeStampedModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    pandascore_id = models.PositiveIntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='teams/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} ({self.game.name})'

    class Meta:
        unique_together = ('game', 'slug')
        ordering = ['name']


class Player(TimeStampedModel):
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    pandascore_id = models.PositiveIntegerField(null=True, blank=True)
    ign = models.CharField(max_length=100, verbose_name='In-game name')
    real_name = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='players/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.ign

    class Meta:
        ordering = ['ign']
