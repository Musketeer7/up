from django.contrib.auth.models import Group
from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from quickstart.serializers import UserSerializer, GroupSerializer, TransactionSerializer #VerificationSerializer
from .models import UserProfile
from .models import PasscodeVerify
from . import models
from . import serializers
from . import permissions

from rest_framework import viewsets
from rest_framework import filters
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import requests
import random
import binascii
import os
import re

from sms.sms import send_message




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


class TransactionViewSet(viewsets.ModelViewSet):
	"""Handles transactions."""

	queryset = models.Transaction.objects.all()
	serializer_class = serializers.TransactionSerializer

	filter_backends = (filters.SearchFilter,)
	search_fields = ('uid',)
	




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

			mobile = request.data['mobile']
			# device_id = request.data['device_id']
			
		except:
			return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

		validate = re.search('^[9]\d{9}$', mobile)
		if validate is None:
			return Response(response_data, status=status.HTTP_402_PAYMENT_REQUIRED)
			
		#check user already
		try:
			user = UserProfile.objects.get(phoneNumber = mobile)
		except UserProfile.DoesNotExist:
			user = ''
		
		#create passcode and send response
		pl = random.sample([1,2,3,4,5,6,7,8,9,0],4)
		passcode = ''.join(str(p) for p in pl)


		if user:
			user.token = ''
			response_data['code'] = 'Re-Registering'
			user.is_verified =  False
			user.device_ident = passcode
			user.save()
			
		else:

			response_data['code'] = 'New-User'
			payload = {"name": "", "password": passcode, "phoneNumber": mobile, "device_ident": passcode}
			r = requests.post("http://127.0.0.1:8000/users/", data=payload)
		

		# SMS api to send passcode
		send_message(mobile, passcode, None, "sending verification passcode.", False)
		"""
		try:
			#create entry in passcode table for verification
			passcode_entry, created = UserProfile.objects.update_or_create(phoneNumber=mobile,  defaults={'device_ident' : passcode,'is_verified' : False})

		except:
			response_data['is_verified']  = "Expire"
			return Response(response_data, status = status.HTTP_403_FORBIDDEN)
		response_data['passcode'] = passcode
		# response_data['code'] = 'Success'
		"""


			
		return Response(response_data, status = status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def verify_and_create(request):
	#verify passcode in PasscodeVerify table
	response_data = {'code' : 'Invalid Data' }
	if request.method == 'POST':
		

		try:
			mobile = request.data['mobile']
			passcode = request.data['passcode']
		except:
			return Response(response_data,status=status.HTTP_400_BAD_REQUEST)

		try:
			# valid = UserProfile.objects.get(phoneNumber = mobile, device_ident = passcode, is_active = Fals	e)
			valid = get_object_or_404(UserProfile, phoneNumber = mobile, device_ident = passcode)
		except PasscodeVerify.DoesNotExist:
			response_data['code'] = 'Invalid/Expired passcode'
			return Response(response_data,status=status.HTTP_401_UNAUTHORIZED)

		if valid:
			if valid.is_active:
				response_data['code'] = 'User already activated'
			else:
				valid.is_active = True
				response_data['code'] = 'Success'
				valid.save()

		"""
		#Generate token 
		token = binascii.hexlify(os.urandom(20)).decode()
		created = ''
		#update or create user device_id and token
		try:
			user,created = UserBase.objects.update_or_create(mobile = mobile,  defaults = {'device_ident' : device_id , 'token' : token ,'is_active' : True})
		except:
			response_data['code'] = 'User creation error'
			return Response(response_data,status=status.HTTP_402_PAYMENT_REQUIRED)

		response_data['code'] = 'Success User created'
		response_data['token'] = token
		"""
		return Response(response_data,status=status.HTTP_201_CREATED)
		


