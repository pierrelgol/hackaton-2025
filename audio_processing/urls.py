from django.urls import path
from . import views

app_name = 'audio_processing'

urlpatterns = [
    path('', views.audio_endpoint, name='audio_endpoint'),
]
