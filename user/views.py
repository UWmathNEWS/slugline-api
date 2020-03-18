from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.http.response import Http404

from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from common.exceptions import APIException
from common.permissions import IsEditor
from common.response import Response
from user.models import SluglineUser, UserSerializer, FORBIDDEN_USERNAMES


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None or password is None:
        raise APIException('AUTH.CREDENTIALS_NONEXISTENT')
    user = authenticate(username=username, password=password)
    if user is None:
        raise APIException('AUTH.CREDENTIALS_INVALID')
    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response()


def update_user(user, request):
    data = request.data
    if 'password' in data:
        # We skip password checking ONLY on a password reset, i.e. an editor is updating an arbitrary user's password
        if user is not request.user and request.user.is_editor:
            pass
        else:
            password = data.get('cur_password', '')
            if not user.check_password(password):
                raise APIException({'user': ['USER.PASSWORD.CURRENT_INCORRECT']})
            del data['cur_password']

    # We set the partial flag as the front-end may not choose to update all fields at once
    serializer = UserSerializer(data=data, instance=user, partial=True)
    serializer.is_valid()
    if len(serializer.errors):
        raise APIException(serializer.errors)
    else:
        try:
            updated_user = serializer.save()
            if 'password' in data:
                update_session_auth_hash(request, updated_user)
            return Response(serializer.data)
        except Exception:
            raise APIException('USER.COULD_NOT_UPDATE')


@api_view(['GET', 'PATCH'])
def single_user_view(request):
    is_authenticated = IsAuthenticated().has_permission(request, None)
    if request.method == 'GET':
        if is_authenticated:
            return Response(UserSerializer(request.user).data)
        else:
            return Response(success=False)
    elif is_authenticated:
        if not request.user.is_staff and not request.user.is_editor and any(['is_editor' in request.data]):
            raise APIException('USER.INSUFFICIENT_PRIVILEGES')
        return update_user(user=request.user, request=request)
    raise exceptions.MethodNotAllowed(request.method)


class UserViewSet(ModelViewSet):
    queryset = SluglineUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsEditor]
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        if SluglineUser.objects.filter(username=request.data['username']).exists():
            raise APIException({'username': ['USER.USERNAME.ALREADY_EXISTS']})
        # max username length; https://docs.djangoproject.com/en/3.0/ref/contrib/auth/
        if len(request.data['username']) > 150:
            raise APIException({'username': ['USER.USERNAME.TOO_LONG']})

        serializer = UserSerializer(data=request.data)
        serializer.is_valid()
        if len(serializer.errors):
            raise APIException(serializer.errors)
        else:
            try:
                serializer.save()
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
            except Exception:
                raise APIException('USER.COULD_NOT_CREATE')

    def retrieve(self, request, *args, **kwargs):
        try:
            return Response(super().retrieve(request, *args, **kwargs).data)
        except Http404:
            raise APIException('USER.DOES_NOT_EXIST')

    def update(self, request, *args, **kwargs):
        try:
            return update_user(user=SluglineUser.objects.get(username=kwargs.get('username', '')), request=request)
        except SluglineUser.DoesNotExist:
            raise APIException('USER.DOES_NOT_EXIST')

    def destroy(self, request, *args, **kwargs):
        try:
            if request.user.username == kwargs.get('username', '') or \
                    SluglineUser.objects.get(username=kwargs.get('username', '')).is_editor:
                raise Exception
            return Response(super().destroy(request, *args, **kwargs).data)
        except Http404:
            raise APIException('USER.DOES_NOT_EXIST')
        except Exception:
            raise APIException('USER.COULD_NOT_DELETE')

    @action(detail=True)
    def query(self, request, username=None):
        return Response(success=len(username) <= 150 and username.lower() not in FORBIDDEN_USERNAMES and
                        not SluglineUser.objects.filter(username=username).exists())
