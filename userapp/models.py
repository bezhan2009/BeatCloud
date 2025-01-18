from django.db import models
from django.contrib.auth.models import User


class UserProfile(User):

    def __str__(self):
        return f"{self.username}"
