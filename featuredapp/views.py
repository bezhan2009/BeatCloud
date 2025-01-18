import logging

from django.shortcuts import (get_object_or_404,
                              Http404)
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from utils.tokens import get_user_id_from_token
from .serializers import *

logger = logging.getLogger("featuredapp.views")


class FeaturedMusicList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        featured_music_list = FeaturedMusic.objects.filter(user=user)
        if not featured_music_list:
            return Response(
                data={'message': 'No music found'},
                status=status.HTTP_200_OK
            )

        serializer = FeaturedMusicSerializer(featured_music_list, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(user_id=user_id)
        serializer = FeaturedMusicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                data={"message": "Music added to favorites successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FeaturedMusicDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(user_id=user_id)
        return get_object_or_404(FeaturedMusic, id=pk, user=user)

    def get(self, request, pk):

        try:
            featured_music = self.get_object(pk, request)
            serializer = FeaturedMusicSerializer(featured_music)
        except Http404:
            return Response(
                data={'message': 'Featured Music not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            featured_music = self.get_object(pk, request)
        except Http404:
            return Response(
                data={'message': 'Featured Music not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        featured_music.delete()

        return Response(
            data={"message": "Music was deleted successfully from favorites"},
            status=status.HTTP_200_OK
        )


class FeaturedAlbumList(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        featured_albums = FeaturedAlbum.objects.filter(user=user)
        if not featured_albums:
            return Response(
                data={'message': 'No featured albums found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = FeaturedAlbumSerializer(featured_albums, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = FeaturedAlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                data={"message": "Album added to favorites successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FeaturedAlbumDetail(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(user_id=user_id)
        return get_object_or_404(FeaturedAlbum, id=pk, user=user)

    def get(self, request, pk):
        try:
            featured_album = self.get_object(pk, request)
            serializer = FeaturedAlbumSerializer(featured_album)
        except Http404:
            return Response(
                data={'message': 'Featured Album not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            featured_album = self.get_object(pk, request)
        except Http404:
            return Response(
                data={'message': 'Featured Album not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        featured_album.delete()
        return Response(
            data={"message": "Album was deleted successfully from favorites"},
            status=status.HTTP_200_OK
        )



