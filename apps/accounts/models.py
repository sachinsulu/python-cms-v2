from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.
    Always define AUTH_USER_MODEL = 'accounts.User' BEFORE first migration.
    Add fields here as needed — this is the safe place to extend the user.
    """
    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
