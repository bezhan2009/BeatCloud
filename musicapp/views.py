from utils.tokens import get_user_id_from_token
from django.shortcuts import get_object_or_404, Http404
from rest_framework import permissions
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger('userapp.views')


class MusicList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        music_list = Music.objects.all()
        serializer = MusicSerializer(music_list, many=True)
        return Response(
                        data=serializer.data,
                        status=status.HTTP_200_OK
                    )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        _user = UserProfile.objects.get(pk=user_id)
        serializer = MusicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=_user)
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

        music_obj.views += 1
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
