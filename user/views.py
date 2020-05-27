from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.db.models import Q
from django.http.response import Http404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from common.filters import SearchableFilterBackend
from common.permissions import IsEditor
from user.models import SluglineUser, UserSerializer, FORBIDDEN_USERNAMES

from math import ceil
from secrets import token_hex
import time


@api_view(["POST"])
def login_view(request):
    if "timeout" in request.session:
        wait = ceil(request.session["timeout"] - time.time())
        if wait > 0:
            raise Throttled(detail=f"AUTH.THROTTLED.{wait}")

    username = request.data.get("username", None)
    password = request.data.get("password", None)

    if username is None or password is None:
        raise AuthenticationFailed("AUTH.CREDENTIALS_NONEXISTENT")

    user = authenticate(username=username, password=password)

    if user is None:
        request.session["attempts"] = request.session.get("attempts", 0) + 1
        if request.session["attempts"] >= 10:
            # exponential timeout for each failed login attempt past the 10th
            timeout = (1 << (request.session["attempts"] - 10)) * 60
            request.session["timeout"] = time.time() + timeout
            raise Throttled(detail=f"AUTH.THROTTLED.{timeout}")
        raise AuthenticationFailed("AUTH.CREDENTIALS_INVALID")

    login(request, user)
    if "attempts" in request.session:
        del request.session["attempts"]
    if "timeout" in request.session:
        del request.session["timeout"]
    return Response(UserSerializer(user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response()


def confirm_password(request):
    if "cur_password" in request.data:
        if not request.user.check_password(request.data["cur_password"]):
            raise APIException({"cur_password": ["USER.PASSWORD.CURRENT_INCORRECT"]})
        del request.data["cur_password"]
    else:
        raise APIException("USER.PASSWORD.CURRENT_REQUIRED")


def update_user(user, request):
    data = request.data
    # We set the partial flag as the front-end may not choose to update all fields at once
    serializer = UserSerializer(data=data, instance=user, partial=True)
    serializer.is_valid()
    # if we're changing roles, or password, confirm password
    if data.get("is_editor") != user.is_editor or "password" in data:
        confirm_password(request)
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
            return update_user(request.user, request)
    else:
        return Response(None)


@api_view(["GET", "POST"])
def reset_password_view(request, token=""):
    timeout = int(token[64:], 16)  # tokens are 64-character random bytes + hex-encoded time
    if int(timeout) - time.time() < 0:
        raise APIException("RESET.TIMED_OUT")
    if request.method == "GET":
        try:
            user = SluglineUser.objects.get(password_reset_token=token)
            return Response(UserSerializer(user).data)
        except SluglineUser.DoesNotExist:
            raise APIException("USER.DOES_NOT_EXIST")
    else:
        user = SluglineUser.objects.get(password_reset_token=token)
        serializer = UserSerializer(
            data={"password": request.data["password"]}, instance=user, partial=True
        )
        serializer.is_valid()

        if len(serializer.errors):
            raise APIException(serializer.errors)
        else:
            user.password_reset_token = ""
            serializer.save()
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
    elif query == "copyeditor":
        return (
            Q(is_staff=False)
            & ~Q(groups__name__in=["Editor"])
            & Q(groups__name__in=["Copyeditor"])
        )
    elif query == "contributor":
        return (
            Q(is_staff=False)
            & ~Q(groups__name__in=["Editor"])
            & ~Q(groups__name__in=["Copyeditor"])
            & Q(groups__name__in=["Contributor"])
        )
    else:
        # return an empty queryset
        return Q(pk__in=[])


class UserViewSet(ModelViewSet):
    queryset = SluglineUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsEditor]
    filter_backends = [SearchableFilterBackend]
    search_fields = ["username", "first_name", "last_name", "writer_name"]
    search_transformers = {
        "name": transform_name,
        "role": transform_role,
        "is": transform_role,
    }
    lookup_field = "username"

    def create(self, request, *args, **kwargs):
        if SluglineUser.objects.filter(username=request.data["username"]).exists():
            raise APIException({"username": ["USER.USERNAME.ALREADY_EXISTS"]})
        # max username length; https://docs.djangoproject.com/en/3.0/ref/contrib/auth/
        if len(request.data["username"]) > 150:
            raise APIException({"username": ["USER.USERNAME.TOO_LONG"]})
        if request.data["is_editor"]:
            confirm_password(request)
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

    @action(detail=True, methods=["POST"])
    def reset_password(self, request, username=None):
        try:
            user = SluglineUser.objects.get(username=username)
            timeout = hex(ceil(time.time() + 21600))[2:]  # Set token to expire after 6 hours
            reset_token = token_hex(32) + timeout  # Make base token 64 characters in length
            user.password_reset_token = reset_token
            user.save()
            return Response(reset_token)
        except SluglineUser.DoesNotExist:
            raise APIException("USER.DOES_NOT_EXIST")
