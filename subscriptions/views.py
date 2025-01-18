import logging

from django.shortcuts import (get_object_or_404,
                              Http404)
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from userapp.models import UserProfile
from musicapp.models import Music
from utils.tokens import get_user_id_from_token
from .serializers import *

logger = logging.getLogger("subscriptions.listens")


class FollowersList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(,
        followers = Followers.objects.filter(user=user)
        if not followers:
            return Response(
                data={"message": "No followers"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = FollowersSerializer(followers, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(,
        serializer = FollowersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowersDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        user_id = get_user_id_from_token(self.request)
        user = UserProfile.objects.get(,
        return get_object_or_404(Followers, pk=pk, user=user)

    def get(self, request, pk):
        try:
            follower = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Follower not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FollowersSerializer(follower)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            follower = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Follower not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        follower.delete()
        return Response(
            data={"message": "Follower deleted"},
            status=status.HTTP_200_OK
        )


class LikesList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(,
        likes = Likes.objects.filter(user=user)
        if not likes:
            return Response(
                data={"message": "No likes"},
                status=status.HTTP_200_OK
            )

        serializer = LikesSerializer(likes, many=True)
        return Response(
            data={serializer.data},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(,
        serializer = LikesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LikesDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        user_id = get_user_id_from_token(self.request)
        user = UserProfile.objects.get(,
        return get_object_or_404(Likes, pk=pk, user=user)

    def get(self, request, pk):
        try:
            like = self.get_object(pk)
            serializer = LikesSerializer(like)
        except Http404:
            return Response(
                data={"message": "Like not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            like = self.get_object(pk)
            like.delete()
        except Http404:
            return Response(
                data={"message": "Like not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data={"message": "Like deleted"},
            status=status.HTTP_200_OK
        )


class SongLikesList(APIView):
    def get(self, request, pk):
        try:
            song = Music.objects.get(id=pk)
            likes = Likes.objects.filter(user=song.user)
            if not likes:
                return Response(
                    data={"message": "No likes"},
                    status=status.HTTP_200_OK
                )
            serializer = LikesSerializer(likes, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Http404:
            return Response(
                data={"message": "Song not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SongCntLikesList(APIView):
    def get(self, request, pk):
        return Response(
            data=Likes.objects.filter(music__likes__music_id=pk).count(),
            status=status.HTTP_200_OK
        )


class SingerCntLikesList(APIView):
    def get(self, request, pk):
        return Response(
            data=Likes.objects.filter(music__singer__singer_id=pk).count(),
            status=status.HTTP_200_OK
        )




