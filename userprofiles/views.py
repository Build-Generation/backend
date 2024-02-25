from django.shortcuts import render, get_object_or_404, HttpResponse
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import *
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .serializers import *
from rest_framework import status
from .models import *
import jwt, datetime, uuid
from .utils import get_authenticated_user, send_change_code, send_email
from django.conf import settings
from datetime import timedelta

# Views

class TestView(GenericAPIView):
    def get(self, request):
        authenticated_user = get_authenticated_user(request)

        serializer = UserSerializer(authenticated_user)
        
        return Response({
            "data": serializer.data,
            "details": "you're online"
        })
    

class SignUpView(GenericAPIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()

        name = request.data.get("name", "")

        bio = request.data.get("bio", "")
        category = request.data.get("category", "")
        sub_category = request.data.get("sub_category", "")
        user_profile = UserProfile.objects.create(user = user, name = name, bio = bio, category = category, sub_category = sub_category)
        
        user_profile.save()
        
        up_serializer = UserProfileSerializer(user_profile)
        merged_data = serializer.data.copy()
        merged_data.update(up_serializer.data)

        code = str(uuid.uuid4()).replace("-", "")[:6]

        send_change_code(user = user, email = request.data["email"], code = code)
        send_email(email = request.data["email"], code = code, username = request.data["username"] )

        return Response(merged_data)

class ChangeVerificationCode(GenericAPIView):
    def post(self, request):
        email = get_authenticated_user(request).email
        user = get_object_or_404(User, email = email)

        user_v, created = VerifyUser.objects.get_or_create(user = user)
        code = str(uuid.uuid4()).replace("-", "")[:6]
        user_v.code = code
        user_v.save()

        
        send_email(email = email, code = code, username = user.username )

        return Response(str(user_v.user))
    
class VerifyUserView(GenericAPIView):
    def get(self, request, code):
        user = get_authenticated_user(request)
        user_profile = get_object_or_404(UserProfile, user = user)

        user_v_code = get_object_or_404(VerifyUser, user = user)

        if code != user_v_code.code:
            return Response({
                "detail": "Incorrect Code"
            }, status = status.HTTP_400_BAD_REQUEST)
        
        user_v_code.delete()
        user_profile.verified = True
        user_profile.save()

        serializer = UserProfileSerializer(UserProfile.objects.get(user = user))
        return Response({
            "detail": "Successfully Verified",
            "data": serializer.data,
        }, status = status.HTTP_200_OK)


class LoginView(GenericAPIView):
    def post(self, request):
        email = request.data.get("email", "")
        password = request.data.get("password", "")

        user = User.objects.filter(email  = email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")
    
        payload = {
            "id" : user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours = 150),
            "iat": datetime.datetime.utcnow()
        }
        try:
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token encoding failed - expired signature"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except jwt.InvalidTokenError:
            return Response({"error": "Token encoding failed - invalid token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True, samesite="None", secure=True)
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Origin"] = "http://localhost:5173"  # Replace with your React app's URL


        response.data =  {
            "jwt": token,
            "auth": request.headers.get("Authorization")
        }

        return response

class GetUpdateUserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, current_profile, *args, **kwargs):
        user = get_authenticated_user(request)

        profile_owner = get_object_or_404(User, username=current_profile)

        user_profile = get_object_or_404(UserProfile, user=profile_owner)

        # Check if the profile is unverified and created more than 4 days ago
        if not user_profile.verified and (timezone.now() - user_profile.date_created) > timedelta(days=4):
            # If the profile owner is checking, return "unverified"
            if user == user_profile.user:
                return Response({
                    "detail": "You have to verify your profile.",
                    "status": "unverified",
                    "data": {
                        "username": user.username,
                        "email": user.email
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)
            # If it's a visitor, return "account not available"
            else:
                return Response({
                    "detail": "Account not available.",
                }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(user_profile)

        user_serializer = UserSerializer(profile_owner)
        merged_data = serializer.data.copy()
        merged_data.update(user_serializer.data)

        return Response(merged_data, status=status.HTTP_200_OK)

def put(self, request, current_profile, *args, **kwargs):
    request.data._mutable = True

    user = get_authenticated_user(request)

    profile_owner = get_object_or_404(User, username=user)
    current_profile = get_object_or_404(User, username=current_profile)

    if current_profile.pk != profile_owner.pk:
        return Response({"details": "unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    user_profile = UserProfile.objects.get(user=profile_owner)

    # Check if the profile is unverified and created more than 4 days ago
    if not user_profile.verified and (timezone.now() - user_profile.date_created) > timedelta(days=4):
        return Response({
            "detail": "You have to verify your profile before updating.",
            "status": "unverified",
        }, status=status.HTTP_401_UNAUTHORIZED)

    request.data["user"] = profile_owner.pk
    serializer = self.serializer_class(user_profile, data=request.data, partial=True)

    if "links" in request.data:
        if len(request.data["links"]) > 7:
            return Response("You can only add up to seven links.", status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        user_serializer = UserSerializer(current_profile)
        merged_data = serializer.data.copy()
        merged_data.update(user_serializer.data)
        return Response({
            "status": status.HTTP_202_ACCEPTED,
            "data": merged_data,
            "detail": "User Profile updated successfully!"
        })
    else:
        return Response(serializer.errors)
