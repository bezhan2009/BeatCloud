from rest_framework import serializers

from featuredapp.models import (FeaturedMusic,
                                FeaturedAlbum,
                                FeaturedPlaylists)
from musicapp.serializers import (MusicSerializer,
                                  AlbumSerializer)
from playlistapp.serializers import PlaylistSerializer
from userapp.models import UserProfile


class FeaturedMusicSerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)  # Подробное представление музыки
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


class FeaturedPlaylistSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)
    playlist = PlaylistSerializer(required=False)

    class Meta:
        model = FeaturedPlaylists
        fields = '__all__'
        read_only_fields = ['user']

