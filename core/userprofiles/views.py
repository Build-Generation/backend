from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import *
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .serializers import *
from rest_framework import status
from .models import *
import jwt, datetime

# Create your views here.

class TestApi(GenericAPIView):
    def get(self, request, *args, **kwargs):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        return Response({
            "detail": "User is authenticated!"
        })

class SignUpView(GenericAPIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()
        user_profile = UserProfile.objects.create(user = user)
        user_profile.save()

        return Response(serializer.data)

class LoginView(GenericAPIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email  = email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")
    
        payload = {
            "id" : user.id ,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes = 60),
            "iat": datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")

        response = Response()

        response.set_cookie(key = "jwt", value = token, httponly=True)
        response.data =  {
            "detail": "logged in"
        }

        return response

        
class GetUpdateUserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get(self, request, current_profile, *args, **kwargs):

        profile_owner = get_object_or_404(User, username = current_profile)
        serializer = self.serializer_class(UserProfile.objects.get(user = profile_owner))

        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, current_profile, *args, **kwargs):

        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        
        user = get_object_or_404(User, id = payload["id"])

        profile_owner = get_object_or_404(User, username = user)

        current_profile = get_object_or_404(User, username = current_profile)

        if current_profile.pk  is not profile_owner.pk:
            return Response({"details": "unauthorized"}, status = status.HTTP_401_UNAUTHORIZED)
        
        request.data["user"] = profile_owner.pk
        user_profile = UserProfile.objects.get( user=profile_owner)
        serializer = self.serializer_class(user_profile, data = request.data)
        if "links" in request.data:
            if len(request.data["links"]) > 7:
                return Response("You can only add up to seven links.",status = status.HTTP_400_BAD_REQUEST)
                

        if serializer.is_valid():
            serializer.save()
            return Response({

                "status": status.HTTP_202_ACCEPTED,
                "data": serializer.data,
                "detail": "User Profile updated successfully!"
            })
        else: 
            return Response(serializer.errors)

class LogoutView(GenericAPIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data={
            "message": "success",
            "details": "logged out!"
        }

        return response
