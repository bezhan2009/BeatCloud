from django.urls import path

from subscriptions import views

urlpatterns = [
    path('followers', views.FollowersSingerList.as_view(), name='followers singer list'),
    path('followers/<int:pk>', views.FollowersSingerDetail.as_view(), name='followers singer detail'),
    path('singer/followers/cnt/<int:pk>', views.SingerCntFollowersList.as_view(), name='singer cnt followers list'),
    path('follow', views.FollowingUserList.as_view(), name='following user list'),
    path('follow/<int:pk>', views.FollowingUserDetail.as_view(), name='following user detail'),
    path('like', views.LikesUserList.as_view(), name='like user list'),
    path('likes/<int:pk>', views.LikesUserDetail.as_view(), name='like user detail'),
    path('song/likes/cnt/<int:pk>', views.SongCntLikesList.as_view(), name='song cnt like list'),
    path('singer/likes/cnt/<int:pk>', views.SingerCntLikesList.as_view(), name='singer like cnt list'),
    path('song/likes/<int:pk>', views.SongUserLikesList.as_view(), name='song like list'),
    path('singer/likes/', views.LikesSingerList.as_view(), name='singer like list'),
]
