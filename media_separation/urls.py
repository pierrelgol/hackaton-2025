from django.urls import path
from . import views

app_name = 'media_separation'

urlpatterns = [
    path('separate/', views.separate_media, name='separate_media'),
    path('list/', views.list_raw_files, name='list_raw_files'),
]
