from rest_framework import serializers

from subscriptions.models import Followers, Likes
from userapp.models import UserProfile


class FollowersSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)

    class Meta:
        model = Followers
        fields = '__all__'


class LikesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)

    class Meta:
        model = Likes
        fields = '__all__'
