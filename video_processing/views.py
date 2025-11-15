from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET', 'POST'])
def video_endpoint(request):
    """
    Video processing endpoint.
    Handle video data from frontend camera/microphone.
    """
    if request.method == 'GET':
        return Response({'message': 'Video processing endpoint'}, status=status.HTTP_200_OK)
    
    # POST request handling for video data
    # Add your video processing logic here
    return Response({'message': 'Video received'}, status=status.HTTP_200_OK)
