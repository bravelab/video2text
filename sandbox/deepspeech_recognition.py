import os
import click
import wave
import numpy as np
from moviepy.editor import VideoFileClip
from tqdm import tqdm
import deepspeech

# Path to DeepSpeech model files
MODEL_FILE_PATH = 'deepspeech-0.9.3-models.pbmm'  # Change this path to your DeepSpeech model
SCORER_FILE_PATH = 'deepspeech-0.9.3-models.scorer'  # Scorer file for DeepSpeech

# DeepSpeech setup
ds_model = deepspeech.Model(MODEL_FILE_PATH)
ds_model.enableExternalScorer(SCORER_FILE_PATH)

def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from video using MoviePy with a progress bar."""
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    duration = int(video_clip.duration)  # in seconds

    pbar = tqdm(total=duration, desc="Extracting audio", unit="sec")

    audio_clip.write_audiofile(output_audio_path, logger=None)

    for second in range(duration):
        pbar.update(1)
    pbar.close()

def preprocess_audio(audio_path):
    """Convert audio to the format expected by DeepSpeech (16kHz, 16-bit mono)."""
    output_audio_path = "converted_audio.wav"
    os.system(f"ffmpeg -i {audio_path} -ar 16000 -ac 1 {output_audio_path}")
    return output_audio_path

def transcribe_with_deepspeech(audio_path):
    """Transcribe speech using DeepSpeech."""
    audio_file = preprocess_audio(audio_path)
    
    with wave.open(audio_file, 'r') as wf:
        assert wf.getframerate() == 16000, "DeepSpeech requires 16kHz audio."
        assert wf.getnchannels() == 1, "DeepSpeech requires mono audio."
        assert wf.getsampwidth() == 2, "DeepSpeech requires 16-bit audio."
        
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        transcription = ds_model.stt(audio)
        
    return transcription

class VideoSpeechExtractor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.audio_path = "extracted_audio.wav"  # Temporary audio file

    def extract_audio(self):
        """Extract audio from video."""
        click.echo(f"Extracting audio from video: {self.video_path}")
        extract_audio_from_video(self.video_path, self.audio_path)

    def transcribe_speech(self):
        """Transcribe the extracted audio to text using DeepSpeech."""
        click.echo(f"Transcribing speech from audio: {self.audio_path}")
        return transcribe_with_deepspeech(self.audio_path)

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

    click.echo(f"Transcribing speech from audio: {audio_path}")
    spoken_text = transcribe_with_deepspeech(audio_path)

    # Save the transcribed text to the specified output file
    with open(output, 'w') as f:
        f.write(spoken_text)
    
    click.echo(f"Transcription complete. Text saved to: {output}")

    # Optionally, remove the temporary extracted audio file
    if os.path.exists("extracted_audio.wav"):
        os.remove("extracted_audio.wav")
 

if __name__ == "__main__":
    video_cli()  # For running video CLI directly