from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
from django.conf import settings
from media_separation.views import separate_media_file

logger = logging.getLogger('video_processing')


@api_view(['GET', 'POST'])
def video_endpoint(request):
    """
    Video processing endpoint.
    Handle video data from frontend camera/microphone.
    Automatically separates audio and video after saving.
    """
    if request.method == 'GET':
        return Response({'message': 'Video processing endpoint'}, status=status.HTTP_200_OK)
    
    # POST request handling for video data
    if 'video' not in request.FILES:
        return Response(
            {'error': 'No video file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    video_file = request.FILES['video']
    
    # Get file info
    file_size = video_file.size
    file_name = video_file.name
    content_type = video_file.content_type
    
    # Save the video file to media directory
    file_path = default_storage.save(
        f'raw/{file_name}',
        ContentFile(video_file.read())
    )
    
    # Get the full path
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # Automatically separate audio and video
    separation_result = separate_media_file(file_name)
    
    if not separation_result['success']:
        # File was saved but separation failed
        return Response({
            'message': 'Video received and saved, but separation failed',
            'file_name': file_name,
            'file_size': file_size,
            'content_type': content_type,
            'saved_path': file_path,
            'full_path': full_path,
            'separation_error': separation_result['error']
        }, status=status.HTTP_200_OK)
    
    # Success - return info about saved file and separated files
    return Response({
        'message': 'Video received, saved, and separated successfully',
        'file_name': file_name,
        'file_size': file_size,
        'content_type': content_type,
        'saved_path': file_path,
        'full_path': full_path,
        'separated': {
            'file_hash': separation_result['file_hash'],
            'video': separation_result['video'],
            'audio': separation_result['audio']
        }
    }, status=status.HTTP_200_OK)
