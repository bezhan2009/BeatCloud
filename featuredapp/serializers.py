from rest_framework import serializers
from userapp.models import UserProfile
from featuredapp.models import (FeaturedMusic,
                                FeaturedAlbum)


class FeaturedMusicSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)

    class Meta:
        model = FeaturedMusic
        fields = '__all__'


class FeaturedAlbumSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)

    class Meta:
        model = FeaturedAlbum
        fields = '__all__'

