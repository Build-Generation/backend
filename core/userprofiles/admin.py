from django.contrib import admin
from .models import *
# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "category", "sub_category", ]

admin.site.register(UserProfile, UserProfileAdmin)