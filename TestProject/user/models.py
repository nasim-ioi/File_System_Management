from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profiles')
    is_owner = models.BooleanField(default=False)
    phone_number = models.CharField(max_length = 50, null = True , blank = True)

    def __str__(self):
        return self.user.username