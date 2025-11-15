from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings


@api_view(['GET', 'POST'])
def audio_endpoint(request):
    """
    Audio processing endpoint.
    Handle audio data from frontend camera/microphone.
    """
    if request.method == 'GET':
        return Response({'message': 'Audio processing endpoint'}, status=status.HTTP_200_OK)
    
    # POST request handling for audio data
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    
    # Get file info
    file_size = audio_file.size
    file_name = audio_file.name
    content_type = audio_file.content_type
    
    # Save the audio file to media directory
    # You can process it here or save for later processing
    file_path = default_storage.save(
        f'raw/{file_name}',
        ContentFile(audio_file.read())
    )
    
    # Get the full path
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # Add your audio processing logic here
    # For example: analyze audio, extract features, etc.
    
    return Response({
        'message': 'Audio received and saved',
        'file_name': file_name,
        'file_size': file_size,
        'content_type': content_type,
        'saved_path': file_path,
        'full_path': full_path,
    }, status=status.HTTP_200_OK)
