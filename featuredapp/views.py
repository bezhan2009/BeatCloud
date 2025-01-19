import logging

from django.shortcuts import (get_object_or_404,
                              Http404)
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from musicapp.models import (Music,
                             Album)
from singerapp.models import Singer
from utils.tokens import get_user_id_from_token
from .serializers import *

logger = logging.getLogger("featuredapp.views")


class FeaturedMusicList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        featured_music_list = FeaturedMusic.objects.prefetch_related("music").filter(user=user)
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
        user = UserProfile.objects.get(id=user_id)
        song_id = request.data.get('song_id', )
        if not song_id:
            return Response(
                data={'message': 'Song id not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            music = Music.objects.get(id=song_id)
        except Music.DoesNotExist:
            return Response(
                data={'message': 'Song does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        if FeaturedMusic.objects.filter(user=user, music=music):
            return Response(
                data={'message': 'Music is already in your favorites'},
                status=status.HTTP_200_OK
            )

        serializer = FeaturedMusicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, music=music)
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
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        return FeaturedMusic.objects.prefetch_related("music").get(id=pk, user=user)

    def get(self, request, pk):
        try:
            featured_music = self.get_object(pk, request)
            serializer = FeaturedMusicSerializer(featured_music)
        except FeaturedMusic.DoesNotExist:
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
        except FeaturedMusic.DoesNotExist:
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
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        featured_albums = FeaturedAlbum.objects.prefetch_related("album").filter(user=user)
        if not featured_albums:
            return Response(
                data={'message': 'No featured albums found'},
                status=status.HTTP_200_OK
            )
        serializer = FeaturedAlbumSerializer(featured_albums, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        album_id = request.data.get("album_id", )
        if not album_id:
            return Response(
                data={'message': 'Album id not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            return Response(
                data={"message": "Album not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if FeaturedAlbum.objects.filter(user=user, album=album):
            return Response(
                data={"message": "Album is already in your favorites"},
                status=status.HTTP_200_OK
            )

        serializer = FeaturedAlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, album=album)
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
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            ), 0

        return FeaturedAlbum.objects.prefetch_related("album").get(id=pk, user=user), 1

    def get(self, request, pk):
        try:
            featured_album, is_success = self.get_object(pk, request)
            if not is_success:
                return featured_album

            serializer = FeaturedAlbumSerializer(featured_album)
        except FeaturedAlbum.DoesNotExist:
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
            featured_album, is_success = self.get_object(pk, request)
            if not is_success:
                return featured_album
        except FeaturedAlbum.DoesNotExist:
            return Response(
                data={'message': 'Featured Album not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        featured_album.delete()
        return Response(
            data={"message": "Album was deleted successfully from favorites"},
            status=status.HTTP_200_OK
        )



