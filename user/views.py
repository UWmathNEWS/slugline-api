from django.contrib.auth import authenticate

from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from user.models import UserSerializer

@api_view(['POST'])
def auth_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None or password is None:
        raise APIException('Username and password are required.')
    user = authenticate(username=username, password=password)
    if user is None:
        raise APIException('Invalid username or password.')
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'user': UserSerializer(user).data,
        'token': token.key
    })
