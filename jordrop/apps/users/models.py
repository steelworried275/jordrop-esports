from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    VISITOR = 'visitor'
    CONTRIBUTOR = 'contributor'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (VISITOR, 'Visitor'),
        (CONTRIBUTOR, 'Contributor'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=VISITOR)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    # --- Role helpers ---

    @property
    def is_contributor(self):
        return self.role in (self.CONTRIBUTOR, self.MODERATOR, self.ADMIN)

    @property
    def is_moderator(self):
        return self.role in (self.MODERATOR, self.ADMIN)

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN
