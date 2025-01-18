from django.urls import path
from featuredapp import views

urlpatterns = [
    path('music/', views.FeaturedMusicList.as_view(), name='featuredmusic'),
    path('music/<int:pk>/', views.FeaturedMusicDetail.as_view(), name='featuredmusicdetail'),

    path('album/', views.FeaturedAlbumList.as_view(), name='featuredalbum'),
    path('album/<int:pk>/', views.FeaturedAlbumDetail.as_view(), name='featuredalbumdetail'),
]
