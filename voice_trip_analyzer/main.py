from voice_recognizer import VoiceRecognizer
from trip_processor import TripProcessor

def main():
    recognizer = VoiceRecognizer()
    processor = TripProcessor()

    print("En attente de commande vocale...")
    voice_text = recognizer.record_and_convert()

    if voice_text:
        print(f"Texte reçu : {voice_text}")
        processor.process_voice_text(voice_text)

if __name__ == "__main__":
    main()
