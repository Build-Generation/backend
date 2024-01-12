from django.db import models
from django.contrib.auth.models import User
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

    profile_pic = models.ImageField(default = "", blank = True, null= True, upload_to = upload_image_path)

    # bg_img = models.ImageField(upload_to="bg-img", null = True, blank = True)



    def __str__(self):
        return str(self.user)
    
    
    # def save(self, *args, **kwargs):
    #     if not self.user:
    #         self.links = []
