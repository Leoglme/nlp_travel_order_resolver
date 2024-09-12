from services.voice_to_text_converter import VoiceToTextConverter

converter = VoiceToTextConverter()
text_from_file = converter.convert_from_audio_file("assets/toulouse-bordeaux.wav")
print(f"Texte extrait du fichier audio : {text_from_file}")

# Pour utiliser le microphone
# text_from_microphone = converter.convert_from_microphone()
# print(f"Texte extrait du microphone : {text_from_microphone}")
