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
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)

	objects = UserProfileManager()

	USERNAME_FIELD = 'phoneNumber'
	REQUIRED_FIELDS = []

	def get_full_name(self):
		"""Used to get a user's full name """

		return str(self.phoneNumber)

	def get_short_name(self):
		"""Used to get a user's short name  """

		return str(self.phoneNumber)

	def __str__(self):
		"""django uses this to convert to string """

		return str(self.phoneNumber)


