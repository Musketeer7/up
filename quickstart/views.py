from django.contrib.auth.models import Group
from django.views.generic import View

from quickstart.serializers import UserSerializer, GroupSerializer #VerificationSerializer
from .models import UserProfile
from .models import PasscodeVerify
from . import models
from . import serializers
from . import permissions

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import random
import binascii
import os
import re



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



# class VerificationViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = models.Verification.objects.all()
#     serializer_class = VerificationSerializer




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

@csrf_exempt
@api_view(['POST'])
def Register(request):
    if request.method == 'POST':
        
        response_data = {'code' : 'Invalid Data' }
        
        #Raise exception in case bad data
        try:
            mobile = request.POST['mobile']
            device_id = request.POST['device_id']
            
        except:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        validate = re.search('^[789]\d{9}$', mobile)
        if validate is None:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            #check user already
        try:
            user = UserProfile.objects.get(phoneNumber = mobile, device_ident = device_id)
        except UserProfile.DoesNotExist:
            user = ''
        
        if user:
            user.token = ''
            response_data['code'] = 'Re-Registering'
            user.is_verified =  False
            user.save()
            
            #create passcode and send response
        pl = random.sample([1,2,3,4,5,6,7,8,9,0],4)
        passcode = ''.join(str(p) for p in pl)

        try:
            #create entry in passcode table for verification
            passcode_entry, created = PasscodeVerify.objects.update_or_create(mobile=mobile,  defaults={'device_ident' : device_id, 'passcode' : passcode,'is_verified' : False})

        except:
            response_data['is_verified']  = "Expire"
            return Response(response_data, status = status.HTTP_400_BAD_REQUEST)
        response_data['passcode'] = passcode
        response_data['code'] = 'Success'
            
            # SMS api to send passcode
        return Response(response_data, status = status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def verify_and_create(request):
    #verify passcode in PasscodeVerify table
    response_data = {'code' : 'Invalid Data' }
    if request.method == 'POST':
        try:
            mobile = request.POST['mobile']
            device_id = request.POST['device_id']
            passcode = request.POST['passcode']
        except:
            return Response(response_data,status=status.HTTP_400_BAD_REQUEST)

        try:
            valid = PasscodeVerify.objects.get(mobile = mobile, device_ident = device_id , passcode = passcode, is_verified = False)
        except PasscodeVerify.DoesNotExist:
            response_data['code'] = 'Invalid/Expired passcode'
            return Response(response_data,status=status.HTTP_400_BAD_REQUEST)

        if valid:
            valid.is_verified = True
            valid.save()


        #Generate token 
        token = binascii.hexlify(os.urandom(20)).decode()
        created = ''
        #update or create user device_id and token
        try:
            user,created = UserBase.objects.update_or_create(mobile = mobile,  defaults = {'device_ident' : device_id , 'token' : token ,'is_active' : True})
        except:
            response_data['code'] = 'User creation error'
            return Response(response_data,status=status.HTTP_400_BAD_REQUEST)

        response_data['code'] = 'Success User created'
        response_data['token'] = token

        return Response(response_data,status=status.HTTP_201_CREATED)

