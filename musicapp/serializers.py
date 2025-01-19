from rest_framework import serializers

from .models import (
    Album,
    Singer,
    Music,
    Genre
)


class MusicSerializer(serializers.ModelSerializer):
    singer = serializers.PrimaryKeyRelatedField(queryset=Singer.objects.all(), required=False)
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(), required=False)

    class Meta:
        model = Music
        fields = '__all__'
        # read_only_fields = ['is_deleted', 'singer', 'duration']


class AlbumSerializer(serializers.ModelSerializer):
    singer = serializers.PrimaryKeyRelatedField(queryset=Singer.objects.all(), required=False)
    songs = MusicSerializer(many=True, required=False)  # Добавляем связанные песни

    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ['singer']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
