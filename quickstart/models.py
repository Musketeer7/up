from django.db import models

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

# from django.contrib.auth import get_user_model


# Create your models here.


class UserProfileManager(BaseUserManager):
	"""Helps django work with custom user model """

	def create_user(self, password=None, phoneNumber=0):
		"""Creates a new profile object"""

		if not phoneNumber:
			raise ValueError('Users must have an phone number')

		# email = self.normalize_email(email)

		user = self.model(phoneNumber=phoneNumber)

		user.set_password(password)

		user.save(using=self._db)

		return user


	def create_superuser(self, password, phoneNumber=0):
		"""Creates a new supersued"""

		user = self.create_user(password, phoneNumber)

		user.is_superuser = True
		user.is_staff = True

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




class UserProfile(AbstractBaseUser, PermissionsMixin):
	"""Represents a user profile inside our system """

	# email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(max_length=255)
	phoneNumber = models.IntegerField(unique=True, default=0)
	device_ident = models.CharField(max_length = 50)
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


