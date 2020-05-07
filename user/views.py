from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.db.models import Q
from django.http.response import Http404

from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from common.mixins import SearchableFilterBackend
from common.permissions import IsEditor
from user.models import SluglineUser, UserSerializer, FORBIDDEN_USERNAMES


@api_view(["POST"])
def login_view(request):
    username = request.data.get("username", None)
    password = request.data.get("password", None)
    if username is None or password is None:
        raise APIException("AUTH.CREDENTIALS_NONEXISTENT")
    user = authenticate(username=username, password=password)
    if user is None:
        raise APIException("AUTH.CREDENTIALS_INVALID")
    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response()


def update_user(user, request):
    data = request.data
    if "password" in data:
        # We skip password checking ONLY on a password reset, i.e. an editor is updating an arbitrary user's password
        if user is not request.user and request.user.is_editor:
            pass
        else:
            password = data.get("cur_password", "")
            if not user.check_password(password):
                raise APIException({"user": ["USER.PASSWORD.CURRENT_INCORRECT"]})
            del data["cur_password"]

    # We set the partial flag as the front-end may not choose to update all fields at once
    serializer = UserSerializer(data=data, instance=user, partial=True)
    serializer.is_valid()
    if len(serializer.errors):
        raise APIException(serializer.errors)
    else:
        try:
            updated_user = serializer.save()
            if "password" in data:
                update_session_auth_hash(request, updated_user)
            return Response(serializer.data)
        except Exception:
            raise APIException("USER.COULD_NOT_UPDATE")


@api_view(["GET", "PATCH"])
def current_user_view(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return Response(UserSerializer(request.user).data)
        else:
            if (
                not request.user.is_staff
                and not request.user.is_editor
                and any(["is_editor" in request.data])
            ):
                raise APIException("USER.INSUFFICIENT_PRIVILEGES")
            return update_user(user=request.user, request=request)
    else:
        return Response(None)


def transform_name(query):
    *first, last = query.rsplit(" ", 1)
    if len(first):
        return Q(first_name__icontains=first[0]) & Q(last_name__icontains=last)
    else:
        return Q(first_name__icontains=last) | Q(last_name__icontains=last)


def transform_role(query):
    query = query.lower()
    if query == "staff":
        return Q(is_staff=True)
    elif query == "editor":
        return Q(is_staff=False) & Q(groups__name__in=["Editor"])
    elif query == "contributor":
        return Q(is_staff=False) & ~Q(groups__name__in=["Editor"]) & Q(groups__name__in=["Contributor"])
    else:
        return Q(pk__in=[])


class UserViewSet(ModelViewSet):
    queryset = SluglineUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsEditor]
    filter_backends = [SearchableFilterBackend]
    search_fields = ["username", "first_name", "last_name", "writer_name"]
    search_transformers = {
        "name": transform_name,
        "role": transform_role
    }
    lookup_field = "username"

    def create(self, request, *args, **kwargs):
        if SluglineUser.objects.filter(username=request.data["username"]).exists():
            raise APIException({"username": ["USER.USERNAME.ALREADY_EXISTS"]})
        # max username length; https://docs.djangoproject.com/en/3.0/ref/contrib/auth/
        if len(request.data["username"]) > 150:
            raise APIException({"username": ["USER.USERNAME.TOO_LONG"]})

        serializer = UserSerializer(data=request.data)
        serializer.is_valid()
        if len(serializer.errors):
            raise APIException(serializer.errors)
        else:
            try:
                serializer.save()
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
            except Exception:
                raise APIException("USER.COULD_NOT_CREATE")

    def retrieve(self, request, *args, **kwargs):
        try:
            return Response(super().retrieve(request, *args, **kwargs).data)
        except Http404:
            raise APIException("USER.DOES_NOT_EXIST")

    def update(self, request, *args, **kwargs):
        try:
            return update_user(
                user=SluglineUser.objects.get(username=kwargs.get("username", "")),
                request=request,
            )
        except SluglineUser.DoesNotExist:
            raise APIException("USER.DOES_NOT_EXIST")

    def destroy(self, request, *args, **kwargs):
        try:
            if (
                request.user.username == kwargs.get("username", "")
                or SluglineUser.objects.get(
                    username=kwargs.get("username", "")
                ).is_editor
            ):
                raise Exception
            return Response(super().destroy(request, *args, **kwargs).data)
        except Http404:
            raise APIException("USER.DOES_NOT_EXIST")
        except Exception:
            raise APIException("USER.COULD_NOT_DELETE")

    @action(detail=True)
    def query(self, request, username=None):
        if (
            SluglineUser.objects.filter(username=username).exists()
            or username.lower() in FORBIDDEN_USERNAMES
        ):
            raise ValidationError({"username": ["USER.USERNAME.ALREADY_EXISTS"]})
        if len(username) > 150:
            raise ValidationError({"username": ["USER.USERNAME.TOO_LONG"]})
        return Response(None)
