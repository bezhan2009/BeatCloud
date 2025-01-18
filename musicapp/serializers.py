from rest_framework import serializers

from .models import (
    Album,
    Singer,
    Music,
    Genre
)


class AlbumSerializer(serializers.ModelSerializer):
    singer = serializers.PrimaryKeyRelatedField(queryset=Singer.objects.all(), required=False)

    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ['singer']


class MusicSerializer(serializers.ModelSerializer):
    singer = serializers.PrimaryKeyRelatedField(queryset=Singer.objects.all(), required=False)
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(), required=False)

    class Meta:
        model = Music
        fields = '__all__'
        # read_only_fields = ['is_deleted', 'singer', 'duration']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
