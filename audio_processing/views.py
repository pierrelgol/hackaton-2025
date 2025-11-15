from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
from django.conf import settings

logger = logging.getLogger('audio_processing')


@api_view(['GET', 'POST'])
def audio_endpoint(request):
    """
    Audio processing endpoint.
    Handle audio data from frontend camera/microphone.
    """
    if request.method == 'GET':
        logger.info('Audio endpoint GET request received')
        return Response({'message': 'Audio processing endpoint'}, status=status.HTTP_200_OK)
    
    # POST request handling for audio data
    logger.info('Audio endpoint POST request received')
    
    if 'audio' not in request.FILES:
        logger.warning('Audio endpoint: No audio file provided in request')
        return Response(
            {'error': 'No audio file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    
    # Get file info
    file_size = audio_file.size
    file_name = audio_file.name
    content_type = audio_file.content_type
    
    logger.info(f'Processing audio file: {file_name} (size: {file_size} bytes, type: {content_type})')
    
    try:
        # Save the audio file to media directory
        # You can process it here or save for later processing
        file_path = default_storage.save(
            f'raw/{file_name}',
            ContentFile(audio_file.read())
        )
        
        # Get the full path
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        logger.info(f'Audio file saved successfully: {file_path} (full path: {full_path})')
        
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
    except Exception as e:
        logger.error(f'Error processing audio file {file_name}: {str(e)}', exc_info=True)
        return Response(
            {'error': f'Error processing audio file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
