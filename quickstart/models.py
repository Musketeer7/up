from django.db import models

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

from datetime import datetime
import random

from sms.sms import send_message


# from django.contrib.auth import get_user_model


# Create your models here.

def send_rand_key_to_user(recipient, code):
	"""sends the key to user"""
	try:
		text = 'your verification code is' + code
		send_message(recipient, text, None, "", False)
		return True
	except:
		return False

class UserProfileManager(BaseUserManager):
	"""Helps django work with custom user model """

	def create_user(self, password, phoneNumber, device_ident):
		"""Creates a new profile object"""

		if not phoneNumber:
			raise ValueError('Users must have an phone number')



		user = self.model(phoneNumber=phoneNumber, device_ident=device_ident)

		user.set_password(password)

		user.save(using=self._db)

		return user




	def create_superuser(self, password, phoneNumber=0):
		"""Creates a new supersued"""

		user = self.create_user(password, phoneNumber, "0000")

		user.is_superuser = True
		user.is_staff = True
		is_active = True
		user.save(using=self._db)

		return user


	def get_by_natural_key(self,phoneNumber):
		return self.get(phoneNumber = phoneNumber)


	def normalize_email(cls, email):
		"""
		Normalize the address by lowercasing the domain part of the email
		address.
		"""
		email = email or ''
		try:
			email_name, domain_part = email.strip().rsplit('@', 1)
		except ValueError:
			pass
		else:
			email = '@'.join([email_name, domain_part.lower()])
		return email


#Generates the random key
def my_random_key():

	pl = random.sample([1,2,3,4,5,6,7,8,9,0],4)
	passcode = ''.join(str(p) for p in pl)
	return passcode


class UserProfile(AbstractBaseUser, PermissionsMixin):
	"""Represents a user profile inside our system """

	# email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(blank=True, max_length=255)
	phoneNumber = models.CharField(unique=True, default=0, max_length=255)
	device_ident = models.CharField(max_length = 50) #, default=my_random_key
	token = models.CharField(max_length = 50,default = 'xyz')
	is_active = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)

	objects = UserProfileManager()

	USERNAME_FIELD = 'phoneNumber'
	REQUIRED_FIELDS = []

	def is_active_user(self):
		return self.is_active

	def is_vendor(self):
		return self.is_vendor

	def get_full_name(self):
		"""Used to get a user's full name """

		return str(self.phoneNumber)

	def get_short_name(self):
		"""Used to get a user's short name  """

		return str(self.phoneNumber)

	def __str__(self):
		"""django uses this to convert to string """

		return str(self.phoneNumber)




class PasscodeVerify(models.Model):
	mobile = models.IntegerField(primary_key=True)
	device_ident = models.CharField(max_length = 20)
	passcode = models.CharField(max_length = 4,default='0000')
	is_verified = models.BooleanField(default=False)
	created_on = models.DateTimeField(auto_now_add=True)
 
	def __str__(self):
		return (str(self.mobile) + ',' + self.passcode)


class Transaction(models.Model):
	"""for storing transactions."""

	transaction_hash = models.CharField(max_length=255)
	transaction_time = models.DateTimeField(auto_now_add=True, blank=True)
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	uid = models.IntegerField(default=0)


	def __str__(self):
		return (str(self.transaction_time) + ',' + self.transaction_hash)


