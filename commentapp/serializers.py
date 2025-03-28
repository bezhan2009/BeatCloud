from rest_framework import serializers
from .models import Comment
from userapp.models import UserProfile
from musicapp.models import (Music,
                             Album)


class CommentChildrenSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    comment_text = serializers.CharField()
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'comment_text', 'parent']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)
    music = serializers.PrimaryKeyRelatedField(queryset=Music.objects.all(), required=False)
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(), required=False)
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Comment
        fields = '__all__'


class CommentMainSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    comment_text = serializers.CharField()
    parent_id = serializers.IntegerField()
    children = CommentChildrenSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment_text', 'parent_id', 'children']
