from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from user.models import UserSerializer

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None or password is None:
        raise APIException('Username and password are required.')
    user = authenticate(username=username, password=password)
    if user is None:
        raise APIException('Invalid username or password.')
    login(request, user)
    return Response(UserSerializer(user).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response()

@api_view(['GET'])
def auth_view(request):
    if request.user is None or request.user.is_anonymous:
        return Response({
            'authenticated': False
        })
    else:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })
    
