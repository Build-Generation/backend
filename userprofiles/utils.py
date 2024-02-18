from .models import User, VerifyUser
import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail


def get_authenticated_user(request, *args, **kwargs):
    try:

        token = request.headers.get("Authorization")

        if not token:
            raise AuthenticationFailed("Token missing")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")

    user = get_object_or_404(User, id=payload["id"])
    return user

def send_change_code(user, email, code):
    try:

        user_v = VerifyUser.objects.create(user = user, code = code)
        user_v.code = code

        user_v.save()

        return {"detail": "code sent/changed!", "status": 201}

    except:
        return {"detail": "error occured", "status": 400}


def send_email(email, code, username):
    subject = 'Verification Code on Link'
    message = f'''<p>Dear {username} You've successfully created an account</p>
    <br />
    <p>Click <a href="http://127.0.0.1:8000/accounts/verify-user/{code}">here</a> to verify your account</p>
    
    Please note that the url here is the url you're supposed to send the GET request to; its not the url that should be accessed.
    '''
    from_email = 'encrane04@gmail.com'
    recipient_list = [email]
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=message)