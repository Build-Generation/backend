from django.urls import path
from .views import *

urlpatterns = [
    # 首页
    path("", TestView.as_view(), name  = "test"),
    path("signup", SignUpView.as_view(), name = "signup"), 
    path("login", LoginView.as_view(), name = "login"),
    path("userprofile/<str:current_profile>", GetUpdateUserProfileView.as_view(), name = "userprofile-actions"),
    path("change-code", ChangeVerificationCode.as_view(), name = "change-code"),
    path("verify-user/<str:code>", VerifyUserView.as_view(), name = "verify-user"),
]