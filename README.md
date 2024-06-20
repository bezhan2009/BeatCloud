
![GitHub top language](https://img.shields.io/github/languages/top/bezhan2009/BeatCloud) 
![GitHub language count](https://img.shields.io/github/languages/count/bezhan2009/BeatCloud)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/bezhan2009/BeatCloud)
![GitHub repo size](https://img.shields.io/github/repo-size/bezhan2009/BeatCloud)
![GitHub last commit](https://img.shields.io/github/last-commit/bezhan2009/BeatCloud)
![GitHub User's stars](https://img.shields.io/github/stars/bezhan2009?style=social)
<br>
<br>
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-latest-brightgreen)

# BeatCloud

BeatCloud is a modern music streaming application built with Django. It offers all the essential features and functionalities for an immersive music listening experience.

## Features

- **User Authentication & Authorization:** Secure access with JWT.
- **Music Management:** Upload, manage, and stream your favorite tracks.
- **Artist & Album Management:** Organize music by artists and albums.
- **Genre Classification:** Categorize music by genres.
- **Cloud Storage:** Store music files securely using Google Cloud Storage.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/harmonystream.git
   cd harmonystream
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Google Cloud Storage credentials:**

   - Obtain your service account JSON file from Google Cloud.
   - Add the file to your project directory.
   - Update your `settings.py` with the path to your service account file and your Google Cloud Storage bucket name.

5. **Run migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser:**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

8. **Access the admin panel:**

   Open your browser and go to `http://localhost:8000/admin/`. Log in with the superuser account you created.

## API Endpoints

- **Obtain JWT Token:**
  ```http
  POST /api/token/
  ```
  Request body:
  ```json
  {
      "username": "your-username",
      "password": "your-password"
  }
  ```

- **Refresh JWT Token:**
  ```http
  POST /api/token/refresh/
  ```
  Request body:
  ```json
  {
      "refresh": "your-refresh-token"
  }
  ```

- **Music Tracks:**
  - List and create music tracks:
    ```http
    GET /api/music/
    POST /api/music/
    ```
    (Authentication required)
