from django.db import models
from django.contrib.auth.models import User
from apps.games.models import Game

class Article(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('game', 'slug')
        ordering = ['-updated_at']
