from pydub import AudioSegment
from io import BytesIO


class AudioService:
    @staticmethod
    def convert_to_wav(file):
        """
        Convert the input audio file to WAV format with 16kHz sampling rate and mono channel.

        :param file: The audio file (can be any format supported by pydub, e.g. mp3, webm)
        :return: A BytesIO object containing the converted WAV file
        """
        print("Converting audio to WAV format...")
        # Load the audio file using pydub
        audio = AudioSegment.from_file(file)

        # Set the audio properties to 16 kHz sampling rate and mono channel
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export the audio as WAV format into a BytesIO object
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")

        # Move to the beginning of the BytesIO object
        wav_io.seek(0)

        return wav_io
