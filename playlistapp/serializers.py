from rest_framework import serializers

from playlistapp.models import Playlist
from userapp.models import UserProfile
from musicapp.serializers import MusicSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)
    music = MusicSerializer(many=True, required=False)

    class Meta:
        model = Playlist
        fields = '__all__'
        read_only_fields = ['user']



