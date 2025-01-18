from mutagen import File
from datetime import timedelta
from django.core.files.storage import default_storage


def handle_uploaded_file(uploaded_file):
    # Сохраняем файл временно
    path = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)

    try:
        # Используем mutagen для получения информации о файле
        audio = File(path)
        if audio and hasattr(audio.info, 'length'):
            duration_seconds = int(audio.info.length)
            duration = timedelta(seconds=duration_seconds)
            return duration
        else:
            raise ValueError("Unable to determine track length.")
    except Exception as e:
        raise ValueError(f"Error processing file: {e}")
    finally:
        # Удаляем временный файл
        default_storage.delete(path)
