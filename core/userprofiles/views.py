from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import *
from rest_framework.generics import GenericAPIView
from django.contrib.auth.models import User
from .serializers import *
from rest_framework import status

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
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    def post(self, request):
        user = get_object_or_404(User, email = request.data["email"])

        if user.check_password(request.data['password']):
            token, create_token = Token.objects.get_or_create(user)

            if token:
                return Response({
                    "token": token.key
                }, status = status.HTTP_200_OK)
            elif create_token:
                return Response({
                    "token": create_token.key
                }, status = status.HTTP_200_OK)
            else:
                return Response({
                    "error": "couldn't complete this action"
                }, status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "error": "credentials don't match!"
            }, status = status.HTTP_401_UNAUTHORIZED)