# video2text.py

import os
import click
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from tqdm import tqdm


def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from video using MoviePy with a progress bar."""
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    duration = int(video_clip.duration)  # in seconds

    pbar = tqdm(total=duration, desc="Extracting audio", unit="sec")

    # MoviePy doesn't have built-in support for a progress bar during the write_audiofile,
    # so we simulate progress by updating the tqdm bar during the audio extraction.
    def update_progress(current_time):
        pbar.update(1)  # Update by 1 second of progress
        return current_time

    # Hook the progress update into MoviePy's frame processing
    audio_clip.write_audiofile(output_audio_path, logger=None)

    # Manually update the progress bar based on video duration
    for second in range(duration):
        update_progress(second)
    pbar.close()



class VideoSpeechExtractor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.audio_path = "extracted_audio.wav"  # Temporary audio file

    def extract_audio(self):
        """Extract audio from video."""
        click.echo(f"Extracting audio from video: {self.video_path}")
        video_clip = VideoFileClip(self.video_path)
        video_clip.audio.write_audiofile(self.audio_path)

    def transcribe_speech(self):
        """Transcribe the extracted audio to text in Polish."""
        recognizer = sr.Recognizer()

        click.echo(f"Transcribing speech from audio: {self.audio_path}")
        # Load the extracted audio file
        with sr.AudioFile(self.audio_path) as source:
            audio_data = recognizer.record(source)

        try:
            # Recognize speech using Google Web Speech API, specifying Polish language
            text = recognizer.recognize_google(audio_data, language="pl-PL")
            return text
        except sr.UnknownValueError:
            return "Nie można było rozpoznać mowy."
        except sr.RequestError as e:
            return f"Błąd podczas komunikacji z usługą rozpoznawania mowy: {e}"
        
        
    def extract_speech_from_video(self):
        """Extract speech from the video and return transcribed text."""
        # Step 1: Extract audio
        self.extract_audio()

        # Step 2: Transcribe the speech from the audio
        text = self.transcribe_speech()

        # Optionally, remove the temporary audio file
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)

        return text


@click.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('-o', '--output', default='transcribed_text.txt', help='Path to save the extracted speech text.')
def video_cli(video_path, output):
    """
    Extract speech from a video file and save the transcribed text to an output file.
    
    \b
    VIDEO_PATH: The path to the video file from which speech will be extracted.
    """
    extractor = VideoSpeechExtractor(video_path)
    
    # Extract and transcribe the spoken language
    spoken_text = extractor.extract_speech_from_video()
    
    # Save the transcribed text to the specified output file
    with open(output, 'w') as f:
        f.write(spoken_text)
    
    click.echo(f"Transcription complete. Text saved to: {output}")


@click.command()
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('-o', '--output', default='transcribed_audio_text.txt', help='Path to save the extracted speech text from audio.')
def audio_cli(audio_path, output):
    """
    Extract speech from an audio or video file and save the transcribed text to an output file.
    
    \b
    AUDIO_PATH: The path to the audio or video file from which speech will be extracted.
    """
    # Check if the input file is a video (e.g., MP4), then extract audio
    if audio_path.lower().endswith(('.mp4', '.mkv', '.mov', '.avi')):
        extracted_audio_path = "extracted_audio.wav"
        click.echo(f"Extracting audio from video: {audio_path}")
        extract_audio_from_video(audio_path, extracted_audio_path)
        audio_path = extracted_audio_path  # Use the extracted audio for transcription

    recognizer = sr.Recognizer()

    # Progress bar for transcribing the audio
    click.echo(f"Transcribing speech from audio: {audio_path}")
    with sr.AudioFile(audio_path) as source:
        audio_duration = int(source.DURATION)  # Length of the audio in seconds
        chunk_duration = 1  # Set chunk size to 1 second
        offset = 0  # Start at the beginning of the audio
        full_text = ""

        # Display progress bar for transcription
        with tqdm(total=audio_duration, desc="Transcribing", unit="sec") as pbar:
            while offset < audio_duration:
                # Record a 1-second chunk from the audio
                audio_chunk = recognizer.record(source, duration=chunk_duration, offset=offset)
                try:
                    # Recognize the chunk using Google Web Speech API
                    text = recognizer.recognize_google(audio_chunk)
                except sr.UnknownValueError:
                    text = "[Unintelligible]\n"
                except sr.RequestError as e:
                    text = f"[Error: {e}]\n"

                # Append the text to the full transcription
                full_text += text + "\n"

                # Update the progress bar and move to the next chunk
                offset += chunk_duration
                pbar.update(chunk_duration)

    # Save the transcribed text to the specified output file
    with open(output, 'w') as f:
        f.write(full_text)
    
    click.echo(f"Transcription complete. Text saved to: {output}")

    # Optionally, remove the temporary extracted audio file
    if os.path.exists("extracted_audio.wav"):
        os.remove("extracted_audio.wav")
 

if __name__ == "__main__":
    video_cli()  # For running video CLI directly