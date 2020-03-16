from django.contrib.auth import login, logout, authenticate, update_session_auth_hash

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from user.models import SluglineUser, UserSerializer, FORBIDDEN_USERNAMES


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_editor or request.user.is_staff))


class SluglineAPIException(APIException):
    def __init__(self, detail):
        super().__init__(detail={
            'success': False,
            'error': [detail] if isinstance(detail, str) else detail
        })


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None or password is None:
        raise SluglineAPIException('AUTH.CREDENTIALS_NONEXISTENT')
    user = authenticate(username=username, password=password)
    if user is None:
        raise SluglineAPIException('AUTH.CREDENTIALS_INVALID')
    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response()


@api_view(['GET'])
def auth_view(request):
    if request.user is None or not request.user.is_authenticated:
        return Response({
            'authenticated': False
        })
    else:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })


@api_view(['GET'])
@permission_classes([IsEditor])
def list_users_view(request):
    start = int(request.GET.get('start', 0))
    limit = int(request.GET.get('limit', 10))
    return Response(map(lambda u: UserSerializer(u).data, SluglineUser.objects.all()[start:start+limit]))


@api_view(['GET'])
@permission_classes([IsEditor])
def query_user_view(request, username):
    return Response({
        'success': len(username) <= 150 and username.lower() not in FORBIDDEN_USERNAMES and
                   not SluglineUser.objects.filter(username=username).exists()
    })


@api_view(['GET'])
@permission_classes([IsEditor])
def list_user_view(request, username):
    try:
        return Response(UserSerializer(SluglineUser.objects.get(username=username)).data)
    except SluglineUser.DoesNotExist:
        raise SluglineAPIException('USER.DOES_NOT_EXIST')


@api_view(['PUT'])
@permission_classes([IsEditor])
def create_user_view(request):
    if SluglineUser.objects.filter(username=request.data['username']).exists():
        raise SluglineAPIException({'username': ['USER.USERNAME.ALREADY_EXISTS']})
    # max username length; https://docs.djangoproject.com/en/3.0/ref/contrib/auth/
    if len(request.data['username']) > 150:
        raise SluglineAPIException({'username': ['USER.USERNAME.TOO_LONG']})

    serializer = UserSerializer(data=request.data)
    serializer.is_valid()
    if len(serializer.errors):
        raise SluglineAPIException(serializer.errors)
    else:
        try:
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data={
                'success': True,
                'user': serializer.data
            })
        except Exception:
            raise SluglineAPIException('USER.COULD_NOT_CREATE')


def update_user(user, request):
    data = request.data
    if 'password' in data:
        # We skip password checking ONLY on a password reset, i.e. an editor is updating an arbitrary user's password
        if user is not request.user and request.user.is_editor:
            pass
        else:
            password = data.get('cur_password', '')
            if not user.check_password(password):
                raise SluglineAPIException({'user': ['USER.PASSWORD.CURRENT_INCORRECT']})
            del data['cur_password']

    # We set the partial flag as the front-end may not choose to update all fields at once
    serializer = UserSerializer(data=data, instance=user, partial=True)
    serializer.is_valid()
    if len(serializer.errors):
        raise SluglineAPIException(serializer.errors)
    else:
        try:
            updated_user = serializer.save()
            if 'password' in data:
                update_session_auth_hash(request, updated_user)
            return Response({
                'success': True,
                'user': serializer.data
            })
        except Exception:
            raise SluglineAPIException('USER.COULD_NOT_UPDATE')


@api_view(['PATCH'])
@permission_classes([IsEditor])
def update_generic_user_view(request, username):
    try:
        return update_user(user=SluglineUser.objects.get(username=username), request=request)
    except SluglineUser.DoesNotExist:
        raise SluglineAPIException('USER.DOES_NOT_EXIST')


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_view(request):
    if not request.user.is_staff and not request.user.is_editor and any(['is_editor' in request.data]):
        raise SluglineAPIException('USER.INSUFFICIENT_PRIVILEGES')
    return update_user(user=request.user, request=request)


@api_view(['DELETE'])
@permission_classes([IsEditor])
def delete_user_view(request, username):
    try:
        if request.user.username == username or SluglineUser.objects.get(username=username).is_editor:
            raise Exception
        SluglineUser.objects.filter(username=username).delete()
        return Response({
            'success': True
        })
    except SluglineUser.DoesNotExist:
        raise SluglineAPIException('USER.DOES_NOT_EXIST')
    except Exception:
        raise SluglineAPIException('USER.COULD_NOT_DELETE')
