from django.contrib.auth.models import Group
from rest_framework import viewsets
from quickstart.serializers import UserSerializer, GroupSerializer
from .models import UserProfile
from . import models
from . import serializers
from . import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    """Handles creating, reading and updating profiles."""

    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)

class LoginViewSet(viewsets.ViewSet):
    """Log in."""

    serializer_class = AuthTokenSerializer

    def create(self, request):
        """to create a token"""

        return ObtainAuthToken().post(request)


