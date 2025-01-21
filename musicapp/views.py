import logging

from django.db import transaction
from django.shortcuts import get_object_or_404, Http404
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.models import UserProfile
from utils.featured_music import delete_featured_music
from utils.music import (get_release_date,
                         get_audio_info)
from utils.music_duration import handle_uploaded_file
from utils.tokens import get_user_id_from_token
from .serializers import *

logger = logging.getLogger('musicapp.views')


class MusicList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        music_list = Music.objects.filter(is_deleted=False)
        if not music_list:
            return Response(
                data={'message': 'No music found'},
                status=status.HTTP_200_OK)
        serializer = MusicSerializer(music_list, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def post(self, request):
        user_id = get_user_id_from_token(request)
        try:
            _user = UserProfile.objects.get(id=user_id)
            _singer = Singer.objects.get(user=_user)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        response, uploaded_file, duration, album, genres = get_audio_info(request, handle_uploaded_file, Album, Genre, is_patch_method=False)
        if response is not None:
            return response

        # Преобразование release_date
        release_date = get_release_date(request)

        serializer = MusicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                singer=_singer,
                album=album,
                duration=duration,
                release_date=release_date
            )
            music = serializer.instance
            music.genre.set(genres)  # Устанавливаем жанры

            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MusicDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk, is_get_request=False):
        if is_get_request:
            return get_object_or_404(Music, pk=pk, is_deleted=False), 1
        user_id = get_user_id_from_token(self.request)
        try:
            user = UserProfile.objects.get(id=user_id)
            singer = Singer.objects.get(user=user)
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Please Register as a singer'},
                status=status.HTTP_403_FORBIDDEN
            ), 0
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            ), 0
        return get_object_or_404(Music, pk=pk, singer=singer, is_deleted=False), 1

    def get(self, request, pk):
        try:
            music_obj, is_success = self.get_object(pk, is_get_request=True)
            if not is_success:
                return music_obj
        except Http404:
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        music_obj.listens += 1
        music_obj.save()
        serializer = MusicSerializer(music_obj)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            music_obj, is_success = self.get_object(pk)
            if not is_success:
                return music_obj
        except Http404:
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        response, uploaded_file, duration, album, genres = get_audio_info(request, handle_uploaded_file, Album, Genre,
                                                                          music_obj, True)
        if response is not None:
            return response

        serializer = MusicSerializer(music_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(
                audio_file=uploaded_file,
                duration=duration,
                album=album,
            )
            if genres:
                music = serializer.instance
                music.genre.set(genres)  # Устанавливаем жанры

            logger.info(f"Music with ID {pk} updated successfully.")
            return Response(
                data={"message": "Music Successfully updated."},
                status=status.HTTP_200_OK
            )

        logger.error(f"Failed to update address with ID {pk}: {serializer.errors}")
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        try:
            music_obj, is_success = self.get_object(pk)
            if not is_success:
                return music_obj
        except Http404:
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        delete_featured_music(music_obj)
        music_obj.is_deleted = True
        music_obj.save()

        return Response(
            data={"message": "Music successfully removed."},
            status=status.HTTP_200_OK
        )


class MusicRestoreView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk):
        return get_object_or_404(Music, pk=pk, is_deleted=False)

    def patch(self, pk):
        try:
            music_obj = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        music_obj.is_deleted = False
        music_obj.save()

        return Response(
            data={"message": "Music successfully restored."},
            status=status.HTTP_200_OK
        )


class AlbumList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        # Предзагружаем связанные песни
        albums = Album.objects.prefetch_related('songs').all()

        if not albums.exists():
            return Response(
                data={"message": "No albums found"},
                status=status.HTTP_200_OK
            )

        # Сериализуем альбомы вместе с песнями
        serializer = AlbumSerializer(albums, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        try:
            _user = UserProfile.objects.get(id=user_id)
            _singer = Singer.objects.get(user=_user)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        release_date = get_release_date(request)
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(singer=_singer, release_date=release_date)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AlbumDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get_object(self, request, pk, get_request: bool = True):
        user_id = get_user_id_from_token(request)
        singer = None
        try:
            if not get_request:
                user = UserProfile.objects.get(id=user_id)
                singer = Singer.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            ), 0
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer does not exist'},
                status=status.HTTP_404_NOT_FOUND
            ), 0

        if singer is not None and not get_request:
            album = Album.objects.prefetch_related('songs').get(pk=pk, singer=singer)
        else:
            album = Album.objects.prefetch_related('songs').get(pk=pk)

        return album, pk

    def get(self, request, pk):
        try:
            album, album_id = self.get_object(request, pk)
            if not album_id:
                return album

            serializer = AlbumSerializer(album, many=False)
        except Album.DoesNotExist:
            return Response(
                data={"message": "Album not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            album, album_id = self.get_object(request, pk, get_request=False)
            if not album_id:
                return album

        except Album.DoesNotExist:
            return Response(
                data={"message": "Album not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        try:
            album, album_id = self.get_object(request, pk, get_request=False)
            if not album_id:
                return album

        except Album.DoesNotExist:
            return Response(
                data={"message": "Album not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        album.delete()
        return Response(
            data={"message": "Album successfully deleted."},
            status=status.HTTP_200_OK
        )


class GenreList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        genre_list = Genre.objects.all()
        if not genre_list:
            return Response(
                data={"message": "No genres available."},
                status=status.HTTP_200_OK
            )

        serializer = GenreSerializer(genre_list, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class GenreDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk):
        return get_object_or_404(Genre, pk=pk)

    def get(self, request, pk):
        try:
            genre = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Genre not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GenreSerializer(genre, many=False)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            genre = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Genre not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GenreSerializer(genre, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        try:
            genre = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Genre not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        genre.delete()
        return Response(
            data={"message": "Genre successfully deleted."},
            status=status.HTTP_200_OK
        )
