from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base: adds created_at and updated_at to every model that inherits it."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SluggedModel(TimeStampedModel):
    """Abstract base: TimeStamped + a slug field."""
    slug = models.SlugField(max_length=200)

    class Meta:
        abstract = True
