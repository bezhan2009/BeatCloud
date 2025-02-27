import logging

from django.shortcuts import (get_object_or_404,
                              Http404)
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from musicapp.models import (Album,
                             Music)
from musicapp.serializers import (AlbumSerializer,
                                  MusicSerializer)
from utils.tokens import get_user_id_from_token
from .serializers import *

logger = logging.getLogger("singerapp.views")


class SingerList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        singers = Singer.objects.all()
        if not singers:
            return Response(
                data={'message': 'No singers are found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SingerSerializer(singers, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            singer = Singer.objects.get(user=user)
            if singer and singer.is_active is False:
                serializer = SingerSerializer(singer, data=request.data)
                if serializer.is_valid():
                    serializer.save(is_active=True)
                    return Response(
                        data={'message': 'Singer was updated and restored successfully'},
                        status=status.HTTP_200_OK
                    )

                logger.warning(
                    f"Serializer Error updating Singer object\n\tdata = {request.data}\n\terror = {serializer.errors}\n\tuser_id = {user_id}")
                return Response(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif singer:
                serializer = SingerSerializer(singer, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        data={'message': 'Singer updated successfully'},
                        status=status.HTTP_200_OK
                    )
                else:
                    logger.warning(
                        f"Serializer Error updating Singer object\n\tdata = {request.data}\n\terror = {serializer.errors}\n\tuser_id = {user_id}")
                    return Response(
                        data=serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Singer.DoesNotExist:
            pass

        serializer = SingerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                data={"message": "and now you are singer"},
                status=status.HTTP_201_CREATED
            )

        logger.warning(
            f"Serializer Error creating Singer object\n\tdata = {request.data}\n\terror = {serializer.errors}\n\tuser_id = {user_id}")
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SingerDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk):
        user_id = get_user_id_from_token(self.request)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            ), 0
        return get_object_or_404(Singer, pk=pk, user=user, is_active=True), user_id

    @method_decorator(cache_page(60 * 15))
    def get(self, request, pk):
        try:
            singer, user_id = self.get_object(pk)
            serializer = SingerSerializer(singer)
        except Http404:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            singer, user_id = self.get_object(pk)
            if not user_id:
                return
        except Http404:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SingerSerializer(singer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        logger.warning(
            f"Serializer Error updating Singer object\n\tdata = {request.data}\n\terror = {serializer.errors}\n\tuser_id = {user_id}")
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        try:
            singer, user_id = self.get_object(pk)
            if not user_id:
                return
        except Http404:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        singer.is_active = False
        singer.save()
        return Response(
            data={'message': 'Singer deleted successfully'},
            status=status.HTTP_200_OK
        )


class SingerRecovery(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request):
        user_id = get_user_id_from_token(self.request)
        user = UserProfile.objects.get(id=user_id)

        try:
            singer = Singer.objects.get(user=user)
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        singer.is_active = True
        singer.save()
        return Response(
            data={'message': 'Singer recovery successful'},
            status=status.HTTP_200_OK
        )


class SingersAlbumList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    @method_decorator(cache_page(60 * 15))
    def get(self, request, pk):
        try:
            singer = Singer.objects.get(id=pk)
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        albums = Album.objects.filter(singer=singer)
        if not albums:
            return Response(
                data={'message': 'No albums are found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AlbumSerializer(albums, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class SingersMusicList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    @method_decorator(cache_page(60 * 15))
    def get(self, request, pk):
        try:
            singer = Singer.objects.get(id=pk)
        except Singer.DoesNotExist:
            return Response(
                data={'message': 'Singer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        songs = Music.objects.filter(singer=singer)
        if not songs:
            return Response(
                data={'message': 'No songs are found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MusicSerializer(songs, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
