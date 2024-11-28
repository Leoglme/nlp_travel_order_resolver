import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.voice_to_text_converter import VoiceToTextConverter

def test_convert_from_audio_file():
    audio_converter = VoiceToTextConverter()
    file_path = "assets/toulouse-bordeaux.wav"
    with open(file_path, "rb") as file:
        text = audio_converter.convert_from_audio_file(file)
        print(text)

test_convert_from_audio_file()