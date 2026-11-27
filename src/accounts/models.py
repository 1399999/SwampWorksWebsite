from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# how long an emailed "become an admin" link stays valid
ADMIN_TOKEN_LIFETIME = timedelta(hours=48)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # only a hash of the emailed secret is stored, never the secret itself
    admin_token_hash = models.CharField(max_length=64, blank=True)
    admin_token_created = models.DateTimeField(null=True, blank=True)

    @property
    def admin_confirmation_pending(self):
        return bool(
            self.admin_token_hash
            and self.admin_token_created
            and timezone.now() - self.admin_token_created < ADMIN_TOKEN_LIFETIME
        )