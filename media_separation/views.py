from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
import hashlib
import subprocess
from pathlib import Path


def separate_media_file(filename):
    """
    Separate audio and video from a file in the raw folder.
    Returns a dict with success status and file information or error message.
    """
    # Convert MEDIA_ROOT to string if it's a Path object
    media_root = str(settings.MEDIA_ROOT)
    
    # Ensure MEDIA_ROOT exists
    os.makedirs(media_root, exist_ok=True)
    
    # Path to the raw file
    raw_file_path = os.path.join(media_root, 'raw', filename)
    
    if not os.path.exists(raw_file_path):
        return {
            'success': False,
            'error': f'File {filename} not found in raw folder'
        }
    
    try:
        # Generate hash from filename
        file_hash = hashlib.md5(filename.encode()).hexdigest()
        
        # Create output directories
        video_dir = os.path.join(media_root, 'video')
        audio_dir = os.path.join(media_root, 'audio')
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        
        # Output file paths
        video_output = os.path.join(video_dir, f'{file_hash}.mp4')
        audio_output = os.path.join(audio_dir, f'{file_hash}.mp3')
        
        # Extract video (re-encode to mp4)
        video_cmd = [
            'ffmpeg',
            '-i', raw_file_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'copy',
            '-y',  # Overwrite output file
            video_output
        ]
        
        # Extract audio (convert to mp3)
        audio_cmd = [
            'ffmpeg',
            '-i', raw_file_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-ar', '44100',
            '-y',  # Overwrite output file
            audio_output
        ]
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return {
                'success': False,
                'error': 'ffmpeg is not installed or not available in PATH. Please install ffmpeg.'
            }
        
        # Run ffmpeg commands
        video_result = subprocess.run(
            video_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if video_result.returncode != 0:
            return {
                'success': False,
                'error': f'Video extraction failed: {video_result.stderr}'
            }
        
        audio_result = subprocess.run(
            audio_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if audio_result.returncode != 0:
            return {
                'success': False,
                'error': f'Audio extraction failed: {audio_result.stderr}'
            }
        
        # Verify files were created
        if not os.path.exists(video_output):
            return {
                'success': False,
                'error': 'Video file was not created'
            }
        
        if not os.path.exists(audio_output):
            return {
                'success': False,
                'error': 'Audio file was not created'
            }
        
        # Get file sizes
        video_size = os.path.getsize(video_output)
        audio_size = os.path.getsize(audio_output)
        
        return {
            'success': True,
            'file_hash': file_hash,
            'video': {
                'filename': f'{file_hash}.mp4',
                'path': f'video/{file_hash}.mp4',
                'full_path': video_output,
                'size': video_size
            },
            'audio': {
                'filename': f'{file_hash}.mp3',
                'path': f'audio/{file_hash}.mp3',
                'full_path': audio_output,
                'size': audio_size
            }
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Processing timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing file: {str(e)}'
        }


@api_view(['POST'])
def separate_media(request):
    """
    Separate audio and video from a file in the raw folder.
    Expects a filename in the request data.
    """
    filename = request.data.get('filename')
    
    if not filename:
        return Response(
            {'error': 'Filename is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = separate_media_file(filename)
    
    if not result['success']:
        return Response(
            {'error': result['error']}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'Media separated successfully',
        'original_file': filename,
        'file_hash': result['file_hash'],
        'video': result['video'],
        'audio': result['audio']
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_raw_files(request):
    """
    List all files in the raw folder.
    """
    # Convert MEDIA_ROOT to string if it's a Path object
    media_root = str(settings.MEDIA_ROOT)
    raw_dir = os.path.join(media_root, 'raw')
    
    if not os.path.exists(raw_dir):
        return Response({'files': []}, status=status.HTTP_200_OK)
    
    try:
        files = []
        for filename in os.listdir(raw_dir):
            file_path = os.path.join(raw_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files.append({
                    'filename': filename,
                    'size': file_size
                })
        
        return Response({'files': files}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error listing files: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
