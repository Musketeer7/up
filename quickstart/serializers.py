from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . import models

class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'groups', 'phone')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
	"""Transaction Serializer."""

	class Meta:
		model = models.Transaction
		fields = ('transaction_hash', 'transaction_time', 'user', 'uid')




# class VerificationSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = models.Verification
#         fields = ('str')

class UserProfileSerializer(serializers.ModelSerializer):
	"""A serializer for our user profile objects."""

	class Meta:
		model = models.UserProfile
		fields = ('id', 'name', 'password', 'phoneNumber', 'device_ident')
		extra_kwargs = {'password': {'write_only': True}}

	def create(self, validated_data):
		"""Create and return a new user."""

		user = models.UserProfile(
			phoneNumber=validated_data['phoneNumber'],
			name=validated_data['name'],
			device_ident=validated_data['device_ident']
		)

		user.set_password(validated_data['password'])
		user.save()

		return user


