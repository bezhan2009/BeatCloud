import logging

from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from musicapp.models import Music
from singerapp.models import Singer
from utils.tokens import get_user_id_from_token
from .serializers import *

logger = logging.getLogger("subscriptions.views")


def get_singer_from_request(request):
    singer_id = request.data.get("singer_id")
    if not singer_id:
        return Response(
            data={"message": "Missing singer_id"},
            status=status.HTTP_400_BAD_REQUEST,
        ), None

    return None, Singer.objects.get(id=singer_id)


def get_music_from_request(request):
    music_id = request.data.get("music_id")
    if not music_id:
        return Response(
            data={"message": "Missing music_id"},
            status=status.HTTP_400_BAD_REQUEST,
        ), None
    try:
        music = Music.objects.get(id=music_id)
    except Music.DoesNotExist:
        return Response(
            data={"message": "Music not found"},
            status=status.HTTP_404_NOT_FOUND,
        ), None
    return None, music


class FollowersSingerList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        try:
            singer = Singer.objects.get(user=user)
        except Singer.DoesNotExist:
            return Response(
                data={"message": "You\'re not a singer to have followers"},
                status=status.HTTP_404_NOT_FOUND
            )
        followers = Followers.objects.filter(singer=singer)

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


class FollowersSingerDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        user_id = get_user_id_from_token(self.request)
        user = UserProfile.objects.get(id=user_id)
        try:
            singer = Singer.objects.get(user=user)
        except Singer.DoesNotExist:
            raise Singer.DoesNotExist

        return Followers.objects.prefetch_related("singer").get(id=pk, singer=singer)

    def get(self, request, pk):
        try:
            follower = self.get_object(pk)
        except Singer.DoesNotExist:
            return Response(
                data={"message": "You\'re not a singer to have followers"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Followers.DoesNotExist:
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
        except Singer.DoesNotExist:
            return Response(
                data={"message": "You\'re not a singer to have followers"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Followers.DoesNotExist:
            return Response(
                data={"message": "Follower not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        follower.delete()
        return Response(
            data={"message": "Follower deleted successfully"},
            status=status.HTTP_200_OK
        )


class FollowingUserList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        followers = Followers.objects.filter(user=user)

        if not followers:
            return Response(
                data={"message": "No followings"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FollowersSerializer(followers, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        response, singer = get_singer_from_request(request)
        if response is not None:
            return response

        if Followers.objects.filter(user=user, singer=singer):
            return Response(
                data={"message": "Already followed"},
                status=status.HTTP_200_OK
            )

        serializer = FollowersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, singer=singer)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowingUserDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        user_id = get_user_id_from_token(self.request)
        user = UserProfile.objects.get(id=user_id)
        return Followers.objects.prefetch_related("singer").get(user=user, pk=pk)

    def get(self, request, pk):
        try:
            follower = self.get_object(pk)
        except Followers.DoesNotExist:
            return Response(
                data={"message": "Following not found"},
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
        except Followers.DoesNotExist:
            return Response(
                data={"message": "Follower not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        follower.delete()
        return Response(
            data={"message": "Unfollowed successfully"},
            status=status.HTTP_200_OK
        )


class LikesUserList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        likes = Likes.objects.prefetch_related("music").filter(user=user)
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

    def post(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        response, music = get_music_from_request(request)
        if response is not None:
            return response

        if Likes.objects.filter(user=user, music=music):
            return Response(
                data={"message": "Already Liked"},
                status=status.HTTP_200_OK
            )

        serializer = LikesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, music=music)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LikesUserDetail(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        user_id = get_user_id_from_token(self.request)
        user = UserProfile.objects.get(id=user_id)
        return Likes.objects.prefetch_related("music").get(user=user)

    def get(self, request, pk):
        try:
            like = self.get_object(pk)
            serializer = LikesSerializer(like)
        except Likes.DoesNotExist:
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
        except Likes.DoesNotExist:
            return Response(
                data={"message": "Like not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data={"message": "Like deleted"},
            status=status.HTTP_200_OK
        )


class LikesSingerList(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)
        try:
            singer = Singer.objects.get(user=user)
        except Singer.DoesNotExist:
            return Response(
                data={"message": "Singer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        likes = Likes.objects.prefetch_related("music").filter(music__singer=singer)
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


class SongUserLikesList(APIView):
    def get(self, request, pk):
        try:
            song = Music.objects.get(id=pk)
            likes = Likes.objects.filter(music=song)
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
        except Music.DoesNotExist:
            return Response(
                data={"message": "Song not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SongCntLikesList(APIView):
    def get(self, request, pk):
        return Response(
            data={'message': Likes.objects.filter(music__likes__music_id=pk).count()},
            status=status.HTTP_200_OK
        )


class SingerCntLikesList(APIView):
    def get(self, request, pk):
        return Response(
            data={'message': Likes.objects.filter(music__singer__id=pk).count()},
            status=status.HTTP_200_OK
        )


class SingerCntFollowersList(APIView):
    def get(self, request, pk):
        try:
            singer = Singer.objects.get(id=pk)
        except Singer.DoesNotExist:
            return Response(
                data={"message": "Singer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data={'message': Followers.objects.filter(singer=singer).count()},
            status=status.HTTP_200_OK
        )


