from django.contrib import admin
from .models import *
# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "category"]

class VerifyUserProfile(admin.ModelAdmin):
    list_display = ["user", "code"]


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(VerifyUser, VerifyUserProfile)