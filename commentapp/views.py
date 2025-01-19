from django.shortcuts import get_object_or_404
from rest_framework import permissions
from drf_yasg import openapi
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from django.db import transaction
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from utils.tokens import get_user_id_from_token
from utils.commentTree import build_comment_tree
from musicapp.models import (Music,
                             Album)

logger = logging.getLogger('commentapp.views')


class CommentMusicList(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get_object(self, music_id):
        music = get_object_or_404(Music, id=music_id)
        comments = Comment.objects.filter(music=music)
        comments_dict = {comment.id: [] for comment in comments}

        for comment in comments:
            if comment.parent_id:
                comments_dict[comment.parent_id].append(comment)

        main_comments = [comment for comment in comments if not comment.parent_id]
        return main_comments, comments_dict

    def get(self, request, music_id):
        try:
            main_comments, comments_dict = self.get_object(music_id)
            main_comments_tree = [build_comment_tree(comment, comments_dict) for comment in main_comments]
            return Response({'comments': main_comments_tree}, status=status.HTTP_200_OK)
        except Http404:  # Обработка ошибки, если объект не найден
            logger.warning(f"Failed to get comments. Music not found.")
            return Response(
                data={"message": "Music not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'parent_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                'comment_text': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['comment_text']
        ),
        security=[],
    )
    @transaction.atomic
    def post(self, request, music_id):
        try:
            user_id = get_user_id_from_token(request)
            user_profile = UserProfile.objects.get(id=user_id)
            serializer = CommentSerializer(data=request.data)

            if serializer.is_valid():
                parent_comment_id = request.data.get('parent', None)
                music = Music.objects.get(id=music_id)  # Здесь лучше использовать get_object_or_404

                parent_comment = None
                if parent_comment_id:
                    parent_comment = Comment.objects.get(id=parent_comment_id, music=music)

                new_comment = serializer.save(user=user_profile, music=music, parent=parent_comment)

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Comment.DoesNotExist:
            logger.warning("Failed to create a new comment. Parent Comment not found.")
            return Response(
                data={"message": "Parent Comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserProfile.DoesNotExist:
            logger.warning(f"Failed to create a new comment. User profile not found.")
            return Response(
                data={"message": "You have not registered yet"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentAlbumList(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get_object(self, album_id):
        album = get_object_or_404(Album, id=album_id)
        comments = Comment.objects.filter(album=album)
        comments_dict = {comment.id: [] for comment in comments}

        for comment in comments:
            if comment.parent_id:
                comments_dict[comment.parent_id].append(comment)

        main_comments = [comment for comment in comments if not comment.parent_id]
        return main_comments, comments_dict

    def get(self, request, album_id):
        try:
            main_comments, comments_dict = self.get_object(album_id)
            main_comments_tree = [build_comment_tree(comment, comments_dict) for comment in main_comments]
            return Response({'comments': main_comments_tree}, status=status.HTTP_200_OK)
        except Http404:  # Обработка ошибки, если объект не найден
            logger.warning(f"Failed to get comments. Album not found.")
            return Response(
                data={"message": "Album not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'parent': openapi.Schema(type=openapi.TYPE_NUMBER),
                'comment_text': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['comment_text']
        ),
        security=[],
    )
    @transaction.atomic
    def post(self, request, album_id):
        try:
            user_id = get_user_id_from_token(request)
            user_profile = UserProfile.objects.get(id=user_id)
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    album = Album.objects.get(id=album_id)
                except Album.DoesNotExist:
                    return Response(
                        data={"message": "Album not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                parent_comment_id = request.data.get('parent', )

                if parent_comment_id:
                    try:
                        parent_comment = Comment.objects.get(id=parent_comment_id)
                        # Проверяем дополнительные условия
                        if not (parent_comment.album == album or parent_comment.music is None):
                            raise Comment.DoesNotExist
                    except Comment.DoesNotExist:
                        raise Comment.DoesNotExist  # Перехватывается ниже для возврата ошибки

                    # Если всё в порядке, сохраняем комментарий и устанавливаем связь
                    new_comment = serializer.save(user=user_profile, album=album, parent=parent_comment)
                else:
                    # Сохраняем комментарий без родительского
                    serializer.save(user=user_profile, album=album)

                return Response(
                    data=serializer.data,
                    status=status.HTTP_200_OK
                )

            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Comment.DoesNotExist:
            logger.warning(f"Failed to create a new comment. Parent Comment not found.")
            return Response(
                data={"message": "Parent comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserProfile.DoesNotExist:
            logger.warning(f"Failed to create a new comment. User profile not found.")
            return Response(
                data={"message": "You have not registered yet"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, _comment_id):
        try:
            return Comment.objects.get(id=_comment_id)
        except Comment.DoesNotExist:
            logger.warning(f"Failed to get comments. Comment not found.")
            raise Http404({"message": "Comment not found"})
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def delete_comment_chain(self, comment):
        # Recursively delete comment chain
        child_comments = Comment.objects.filter(parent_id=comment.id)
        for child_comment in child_comments:
            self.delete_comment_chain(child_comment)
            child_comment.delete()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        security=[],
    )
    @transaction.atomic
    def delete(self, request, comment_id):
        try:
            user_id = get_user_id_from_token(request)
            user_profile = UserProfile.objects.get(id=user_id)
            comment = Comment.objects.get(id=comment_id, user=user_profile)
            logger.info(f"Attempting to delete comment with ID {comment_id}.")
        except Comment.DoesNotExist:
            logger.warning(f"Failed to delete Comment. Comment with ID {comment_id} not found.")
            return Response(
                data={"message": "Comment Not Found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Delete the entire comment chain
        self.delete_comment_chain(comment)

        # Delete the parent comment
        comment.delete()

        return Response(
            data={"message": "Comment deleted successfully"},
            status=status.HTTP_200_OK
        )
