from django.urls import path

from singerapp import views

urlpatterns = [
    path('', views.SingerList.as_view(), name='singer-list'),
    path('<int:pk>/', views.SingerDetail.as_view(), name='singer-detail'),
    path('restore/', views.SingerRecovery.as_view(), name='singer-recovery'),
]
