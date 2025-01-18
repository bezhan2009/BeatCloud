from utils.tokens import get_user_id_from_token
from django.shortcuts import get_object_or_404
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


class UserProfileList(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    def post(self, request):
        data = {
            'username': request.data['username'],
            'password': request.data['password'],
            'email': request.data['email'],
        }
        serializer = UserProfileSerializer(data=data)
        if serializer.is_valid():
            user = UserProfile.objects.create_user(**data)
            refresh = RefreshToken.for_user(user)
            logger.info(f"New user created with ID {user.id}.")
            return Response(
                data={
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id
                }, status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileDetails(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_user(self, _id):
        return get_object_or_404(UserProfile, id=_id)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        security=[],
    )
    def get(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = self.get_user(user_id)
            logger.info(f"User with ID {user_id} retrieved successfully.")
        except UserProfile.DoesNotExist:
            logger.warning(f"Failed to retrieve user. User with ID {user_id} not found.")
            return Response(
                data={"message": "User Not Found"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserProfileSerializer(user, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['username']
        ),
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        security=[],
    )
    def put(self, request):
        user_id = get_user_id_from_token(request)
        try:
            user = self.get_user(user_id)
            logger.info(f"Attempting to update user with ID {user_id}.")
        except UserProfile.DoesNotExist:
            logger.warning(f"Failed to update user. User with ID {user_id} not found.")
            return Response(
                data={"message": "User Not Found."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if 'password' in request.data or 'is_deleted' in request.data or 'is_superuser' in request.data:
            return Response(
                data={"message": "Changing password, is_superuser is not allowed."},
                status=status.HTTP_403_FORBIDDEN
            )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User with ID {user_id} updated successfully.")
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        logger.error(f"Failed to update user with ID {user_id}: {serializer.errors}")
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
