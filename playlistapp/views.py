import logging

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from guardian.shortcuts import (get_perms,
                                assign_perm)
from musicapp.models import (Music)
from playlistapp.models import PlaylistMusic
from utils.tokens import get_user_id_from_token
from utils.perms_playlist import (PlaylistPerms,
                                  get_playlist_perms_obj,
                                  get_admin_perms,
                                  get_basic_perms)
from .serializers import *

logger = logging.getLogger('playlistapp.views')


def get_playlist_perms(request, pk, user=None):
    if not user:
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
    try:
        playlist = Playlist.objects.prefetch_related("music").get(pk=pk)
    except Playlist.DoesNotExist:
        raise Playlist.DoesNotExist

    perms = get_playlist_perms_obj(user, playlist)

    return perms


def get_music_obj(request):
    music_id = request.data.get('music_id')
    if not music_id:
        return Response(
            data={'message': 'Missing music id'},
            status=status.HTTP_400_BAD_REQUEST
        ), None

    try:
        music_track = get_object_or_404(Music, pk=music_id)
    except Http404:
        return Response(
            data={'message': 'Music does not exist'},
            status=status.HTTP_404_NOT_FOUND
        ), None

    return None, music_track


def get_user(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            data={'message': 'Missing user id'},
            status=status.HTTP_400_BAD_REQUEST
        ), None

    try:
        return None, UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response(
            data={'message': 'User does not exist'},
            status=status.HTTP_404_NOT_FOUND
        ), None


def get_user_from_token(request):
    return UserProfile.objects.get(id=get_user_id_from_token(request))


class PlaylistUserView(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        try:
            user_id = get_user_id_from_token(request)
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        playlists = Playlist.objects.prefetch_related("music").filter(user=user)
        if not playlists:
            return Response(
                data={'message': 'You don\'t have any playlists yet'},
                status=status.HTTP_200_OK
            )
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        try:
            user_id = get_user_id_from_token(request)
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                data={'message': 'User does not exist'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = PlaylistSerializer(data=request.data)
        if serializer.is_valid():
            playlist = serializer.save(user=user)
            playlist_perms = PlaylistPerms(user, playlist)
            playlist_perms.set_admin_perms()

            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PlaylistUserDetailView(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        try:
            playlist_perms = get_playlist_perms(request, pk)
            playlist = playlist_perms.get_playlist()
            if playlist is None:
                raise Playlist.DoesNotExist

            serializer = PlaylistSerializer(playlist, many=False)
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            playlist_perms = get_playlist_perms(request, pk)
            playlist = playlist_perms.get_playlist()
            if playlist is None or not playlist_perms.check_perms('change_playlist'):
                raise Playlist.DoesNotExist
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaylistSerializer(playlist, data=request.data)
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
            playlist_perms = get_playlist_perms(request, pk)
            playlist = playlist_perms.get_playlist()
            if playlist is None or not playlist_perms.check_perms('delete_playlist'):
                raise Playlist.DoesNotExist
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        playlist.delete()
        return Response(
            data={'message': 'Playlist deleted successfully'},
            status=status.HTTP_200_OK
        )


class PlaylistUserMusicDetailView(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def patch(self, request, pk):
        try:
            playlist_perms = get_playlist_perms(request, pk)
            playlist = playlist_perms.get_playlist()
            if playlist is None or not playlist_perms.check_perms('add_music'):
                raise Playlist.DoesNotExist
        except Http404:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        response, music_track = get_music_obj(request)
        if response is not None:
            return response

        playlist_music, created = PlaylistMusic.objects.get_or_create(
            playlist=playlist, music=music_track
        )
        if not created:
            playlist_music.count += 1
            playlist_music.save()

        return Response(
            data={'message': 'Music added to playlist'},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            playlist_perms = get_playlist_perms(request, pk)
            playlist = playlist_perms.get_playlist()
            if playlist is None or not playlist_perms.check_perms('remove_music'):
                raise Playlist.DoesNotExist
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        response, music_track = get_music_obj(request)
        if response is not None:
            return response

        try:
            playlist_music = PlaylistMusic.objects.get(playlist=playlist, music=music_track)
            if playlist_music.count > 1:
                playlist_music.count -= 1
                playlist_music.save()
            else:
                playlist_music.delete()
        except PlaylistMusic.DoesNotExist:
            return Response(
                data={'message': 'Music not found in playlist'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data={'message': 'Music removed from playlist'},
            status=status.HTTP_200_OK
        )


class PlaylistMusicView(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (AllowAny, )

    def get(self, request):
        playlists = Playlist.objects.prefetch_related("music").filter(private=False)
        if not playlists:
            return Response(
                data={'message': 'No playlists found'},
                status=status.HTTP_200_OK
            )

        serializer = PlaylistSerializer(playlists, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class PlaylistMusicDetailView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            playlists = Playlist.objects.prefetch_related("music").get(private=False, id=pk)
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        playlists.listens = playlists.listens + 1

        serializer = PlaylistSerializer(playlists, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class PlaylistPermissions(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk):
        response, user = get_user(request)
        if response is not None:
            return response

        sender_user = get_user_from_token(request)

        if user == sender_user:
            return Response(
                data={'message': 'You cannot set perms to yourself'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            playlist_perms = get_playlist_perms(request, pk, user)
            playlist_sender_perms = get_playlist_perms(request, pk, sender_user)
            if not playlist_sender_perms.check_perms("set_playlist_perms"):
                return Response(
                    data={'message': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        playlist_perms.set_basic_perms()
        return Response(
            data={'message': 'Playlist permissions updated successfully'},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        response, user = get_user(request)
        if response is not None:
            return response

        sender_user = get_user_from_token(request)

        try:
            playlist_perms = get_playlist_perms(request, pk, user)
            playlist_sender_perms = get_playlist_perms(request, pk, sender_user)
            if not playlist_sender_perms.check_perms("remove_playlist_perms"):
                return Response(
                    data={'message': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        if sender_user != user:
            playlist_perms.reset_perms()
            return Response(
                data={'message': 'User permissions reset successfully'},
                status=status.HTTP_200_OK
            )

        return Response(
            data={'message': 'You cannot reset your own permission for a playlist'},
            status=status.HTTP_403_FORBIDDEN
        )


class PlaylistPermissionsSpecific(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        response, user = get_user(request)
        if response is not None:
            return response

        sender_user = get_user_from_token(request)

        try:
            playlist_perms = get_playlist_perms(request, pk, user)
            playlist_sender_perms = get_playlist_perms(request, pk, sender_user)
            if not playlist_sender_perms.check_perms("view_playlist_perms"):
                return Response(
                    data={'message': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data={'message': playlist_perms.get_user_perms()}
        )

    def patch(self, request, pk):
        response, user = get_user(request)
        if response is not None:
            return response

        sender_user = get_user_from_token(request)

        if user == sender_user:
            return Response(
                data={'message': 'You cannot set perms to yourself'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            playlist_perms = get_playlist_perms(request, pk, user)
            playlist_sender_perms = get_playlist_perms(request, pk, sender_user)
            if not playlist_sender_perms.check_perms("set_playlist_perms"):
                return Response(
                    data={'message': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        perm = request.data.get('permission')
        if perm is None:
            return Response(
                data={'message': 'Permission missing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if perm not in get_admin_perms() or perm not in get_basic_perms():
            return Response(
                data={'message': 'Invalid permission'},
                status=status.HTTP_400_BAD_REQUEST
            )

        playlist_perms.add_perm(perm)
        return Response(
            data={'message': 'Permission updated successfully'},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        response, user = get_user(request)
        if response is not None:
            return response

        sender_user = get_user_from_token(request)

        try:
            playlist_perms = get_playlist_perms(request, pk, user)
            playlist_sender_perms = get_playlist_perms(request, pk, sender_user)
            if not playlist_sender_perms.check_perms("remove_playlist_perms"):
                return Response(
                    data={'message': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Playlist.DoesNotExist:
            return Response(
                data={'message': 'Playlist does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        perm = request.data.get('permission')
        if perm is None:
            return Response(
                data={'message': 'Permission missing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if perm not in get_admin_perms() or perm not in get_basic_perms():
            return Response(
                data={'message': 'Invalid permission'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if sender_user != user:
            playlist_perms.remove_perms(perm)
            return Response(
                data={'message': 'Permission removed successfully'},
                status=status.HTTP_200_OK
            )

        return Response(
            data={'message': 'You cannot remove your own permission for a playlist'},
            status=status.HTTP_403_FORBIDDEN
        )


class PlaylistRestorePermission(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request, pk):
        playlist_perms = get_playlist_perms(request, pk)
        user = playlist_perms.get_user()
        playlist_user = playlist_perms.get_playlist_user()
        if user != playlist_user:
            return Response(
                data={'message': 'You\'re not the owner of the playlist'},
                status=status.HTTP_403_FORBIDDEN
            )

        playlist_perms.set_admin_perms()
        return Response(
            data={'message': 'Admin permissions updated successfully'},
            status=status.HTTP_200_OK
        )
