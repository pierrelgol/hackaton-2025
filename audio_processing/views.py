from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET', 'POST'])
def audio_endpoint(request):
    """
    Audio processing endpoint.
    Handle audio data from frontend camera/microphone.
    """
    if request.method == 'GET':
        return Response({'message': 'Audio processing endpoint'}, status=status.HTTP_200_OK)
    
    # POST request handling for audio data
    # Add your audio processing logic here
    return Response({'message': 'Audio received'}, status=status.HTTP_200_OK)
