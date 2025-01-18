from rest_framework import serializers
from singerapp.models import (Singer,
                              UserProfile)


class SingerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)

    class Meta:
        model = Singer
        fields = '__all__'
        read_only_fields = ('is_active',)
