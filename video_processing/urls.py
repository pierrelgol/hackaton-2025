from django.urls import path
from . import views

app_name = 'video_processing'

urlpatterns = [
    path('', views.video_endpoint, name='video_endpoint'),
]
