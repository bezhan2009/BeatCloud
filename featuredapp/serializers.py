from rest_framework import serializers

from musicapp.serializers import (MusicSerializer,
                                  AlbumSerializer)
from musicapp.models import (Music,
                             Album)
from userapp.models import UserProfile
from featuredapp.models import (FeaturedMusic,
                                FeaturedAlbum)


class FeaturedMusicSerializer(serializers.ModelSerializer):
    music = MusicSerializer()  # Подробное представление музыки
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)

    class Meta:
        model = FeaturedMusic
        fields = '__all__'
        read_only_fields = ['music']


class FeaturedAlbumSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)
    album = AlbumSerializer(required=False)

    class Meta:
        model = FeaturedAlbum
        fields = '__all__'
        read_only_fields = ['user']

