from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import *
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .serializers import *
from rest_framework import status
from .models import *

# Create your views here.

class TestApi(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        
        return Response({
            "detail": "User is authenticted!"
        })


class SignUpView(GenericAPIView):
    def post(self, request):
        
        if request.data["password"] != request.data["confirm_password"]:
            return Response({
                "error":"Password and confirm password does not match"},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            
            user = serializer.save()
            token = Token.objects.get(user=user)
            user_profile = UserProfile.objects.create(user = user)
            user_profile.save()
            return Response({
                'token': token.key,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    
    def post(self, request):
        user = get_object_or_404(User, email = request.data["email"])

        
        if user.check_password(request.data['password']):
            
            token, create_token = Token.objects.get_or_create(user = user.pk)
            

            if token:
                return Response({
                    "token": token.key,
                    "details": "user's credentials were correct"
                }, status = status.HTTP_200_OK)
            elif create_token:
                return Response({
                    "token": create_token.key,
                    "details": "user's credentials were correct"
                }, status = status.HTTP_200_OK)
            else:
                return Response({
                    "error": "couldn't complete this action"
                }, status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "error": "credentials don't match!"
            }, status = status.HTTP_401_UNAUTHORIZED)

        
class GetUpdateUserProfileView(RetrieveUpdateAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UserProfileSerializer

    def get(self, request, user, *args, **kwargs):
        profile_owner = get_object_or_404(User, username = user)
        serializer = self.serializer_class(UserProfile.objects.get(user = profile_owner))

        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, user, *args, **kwargs):
        profile_owner = get_object_or_404(User, username = user)
        if request.user.pk  is not profile_owner.pk:
            return Response({"details": "unauthorized"}, status = status.HTTP_401_UNAUTHORIZED)
        request.data["user"] = request.user.pk
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




