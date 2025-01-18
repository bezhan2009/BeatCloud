import logging
import datetime

from datetime import date
from django.shortcuts import get_object_or_404, Http404
from rest_framework import permissions
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from userapp.models import UserProfile
from utils.tokens import get_user_id_from_token
from utils.music_duration import handle_uploaded_file
from .serializers import *

logger = logging.getLogger('musicapp.views')


class MusicList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        music_list = Music.objects.all()
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

        uploaded_file = request.FILES.get('audio_file', )
        if not uploaded_file:
            return Response(
                data={"message": "Audio not uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            duration = handle_uploaded_file(uploaded_file)
        except ValueError as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        album_id = request.data.get('album_id', )
        try:
            album = Album.objects.get(pk=album_id)
        except Album.DoesNotExist:
            album = None

        genre_ids = request.data.getlist('genre_ids', [])  # Получаем список жанров
        genres = Genre.objects.filter(pk__in=genre_ids)

        # Преобразование release_date
        release_date = request.data.get('release_date', None)
        if release_date:
            try:
                release_date = datetime.fromisoformat(release_date).date()
            except ValueError:
                return Response(
                    data={"message": "Invalid release_date format. Use 'YYYY-MM-DD'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            release_date = date.today()  # Устанавливаем текущую дату

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

    def get_object(self, pk):
        return get_object_or_404(Music, pk=pk, is_deleted=False)

    def get(self, request, pk):
        try:
            music_obj = self.get_object(pk)
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

    def put(self, request, pk):
        try:
            music_obj = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MusicSerializer(music_obj, data=request.data)
        if serializer.is_valid():
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
            music_obj = self.get_object(pk)
        except Http404:
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )

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
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.AllowAny, )

    def get(self, request):
        albums = Album.objects.all()
        if not albums:
            return Response(
                data={"message": "No albums found"},
                status=status.HTTP_200_OK
            )

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

        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(singer=_singer)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
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

