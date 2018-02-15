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


# class VerificationSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = models.Verification
#         fields = ('str')



class UserProfileSerializer(serializers.ModelSerializer):
	"""A serializer for our user profile objects."""

	class Meta:
		model = models.UserProfile
		fields = ('id', 'name', 'password', 'phoneNumber')
		extra_kwargs = {'password': {'write_only': True}}

	def create(self, validated_data):
		"""Create and return a new user."""

		user = models.UserProfile(
			phoneNumber=validated_data['phoneNumber'],
			name=validated_data['name']
		)

		user.set_password(validated_data['password'])
		user.save()

		return user


