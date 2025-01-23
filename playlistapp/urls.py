from django.urls import path

from playlistapp import views

urlpatterns = [
    path('', views.PlaylistMusicView.as_view(), name='playlist music view'),
    path('<int:pk>', views.PlaylistMusicDetailView.as_view(), name='playlist music view'),
    path('my/', views.PlaylistUserView.as_view(), name='my playlist view'),
    path('my/<int:pk>', views.PlaylistUserDetailView.as_view(), name='my playlist detail view'),
    path('my/music/<int:pk>', views.PlaylistUserMusicDetailView.as_view(), name='playlist music view'),
    path('my/permissions/<int:pk>', views.PlaylistPermissions.as_view(), name='playlist permissions view'),
    path('my/permissions/sp/<int:pk>', views.PlaylistPermissionsSpecific.as_view(), name='playlist permissions specific'),
    path('my/permissions/restore/<int:pk>', views.PlaylistRestorePermission.as_view(), name='playlist permissions restore'),

]
