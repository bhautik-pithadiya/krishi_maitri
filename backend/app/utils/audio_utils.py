import wave
import io
import base64

def wav_to_bytes(wav_file_path: str) -> bytes:
    """
    Convert a WAV file to bytes.
    
    Args:
        wav_file_path (str): Path to the WAV file
        
    Returns:
        bytes: The WAV file content as bytes
    """
    try:
        with open(wav_file_path, 'rb') as wav_file:
            # also save it in a file
            
            return wav_file.read()
    except Exception as e:
        raise Exception(f"Error reading WAV file: {str(e)}")

def wav_to_base64(wav_file_path: str) -> str:
    """
    Convert a WAV file to base64 string.
    
    Args:
        wav_file_path (str): Path to the WAV file
        
    Returns:
        str: Base64 encoded string of the WAV file
    """
    try:
        with open(wav_file_path, 'rb') as wav_file:
            wav_bytes = wav_file.read()
            return base64.b64encode(wav_bytes).decode('utf-8')
    except Exception as e:
        raise Exception(f"Error converting WAV to base64: {str(e)}")

def bytes_to_wav(audio_bytes: bytes, output_path: str):
    """
    Save audio bytes as a WAV file.
    
    Args:
        audio_bytes (bytes): Audio data in bytes
        output_path (str): Path where the WAV file should be saved
    """
    try:
        with open(output_path, 'wb') as wav_file:
            wav_file.write(audio_bytes)
    except Exception as e:
        raise Exception(f"Error saving WAV file: {str(e)}") 