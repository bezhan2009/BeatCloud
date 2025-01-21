import datetime

from datetime import date
from rest_framework.response import Response
from rest_framework import status


def get_release_date(request):
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

    return release_date


def get_audio_info(request, handle_uploaded_file, Album, Genre, music_obj=None, is_patch_method: bool = False):
    uploaded_file = request.FILES.get('audio_file', )
    print(uploaded_file)
    if not is_patch_method:
        if not uploaded_file:
            return Response(
                data={"message": "Audio not uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            ), None, None, None, None
    if uploaded_file:
        try:
            duration = handle_uploaded_file(uploaded_file)
        except ValueError as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ), None, None, None, None
    else:
        duration = music_obj.duration
        uploaded_file = music_obj.audio_file

    album_id = request.data.get('album_id', )
    try:
        album = Album.objects.get(pk=album_id)
    except Album.DoesNotExist:
        album = None

    genre_ids = request.data.getlist('genre_ids', [])  # Получаем список жанров
    genres = Genre.objects.filter(pk__in=genre_ids)

    return None, uploaded_file, duration, album, genres

