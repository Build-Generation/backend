from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
# Create your models here.
def upload_image_path(instance, filename):
    # Define the upload path for images
    return f"images/{filename}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(max_length=100)
    bio_title = models.CharField(max_length= 100, null = True, blank =True)
    bio = models.TextField()
    category = models.CharField(max_length = 100)
    sub_category = models.CharField(max_length=100, blank = True, null = True)

    links = models.JSONField(default = dict)

    header = models.CharField(max_length = 250, blank = True, null = True)


    date_created = models.DateTimeField(auto_now_add = True)
    verified = models.BooleanField(default = False)

    def __str__(self):
        return str(self.user)
    
class VerifyUser(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    code = models.CharField(max_length = 6)

    def __str__(self):

        return str(self.user)
