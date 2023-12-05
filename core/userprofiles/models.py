from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(max_length=100)
    bio = models.TextField()
    category = models.CharField(max_length = 100)
    sub_category = models.CharField(max_length=100, blank = True, null = True)

    def __str__(self):
        return str(self.user)