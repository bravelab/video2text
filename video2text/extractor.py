import os
import click
import wave
from moviepy.editor import VideoFileClip
from tqdm import tqdm
from google.cloud import speech, storage

# Function to extract audio from video
def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from video using MoviePy with a progress bar."""
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    duration = int(video_clip.duration)  # in seconds

    pbar = tqdm(total=duration, desc="Extracting audio", unit="sec")
    
    # Extract audio and update progress bar manually
    audio_clip.write_audiofile(output_audio_path, logger=None)
    
    for second in range(duration):
        pbar.update(1)
    pbar.close()

# Function to convert audio to required format (16kHz, 16-bit mono WAV)
def preprocess_audio(audio_path):
    """Convert audio to 16kHz, 16-bit mono PCM WAV for Google Cloud Speech."""
    output_audio_path = "converted_audio.wav"
    os.system(f"ffmpeg -i {audio_path} -ac 1 -ar 16000 {output_audio_path}")
    return output_audio_path

# Function to upload audio to Google Cloud Storage
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    click.echo(f"File {source_file_name} uploaded to {destination_blob_name}.")
    
    return f"gs://{bucket_name}/{destination_blob_name}"

# Function to transcribe long audio using GCS URI
def transcribe_long_audio_google_cloud_gcs(gcs_uri, language_code="pl-PL"):
    """Transcribe long audio using Google Cloud Speech-to-Text and GCS URI."""
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    click.echo("Waiting for operation to complete...")
    response = operation.result(timeout=180)  # Wait up to 3 minutes

    # Extract the transcription from the response
    transcribed_text = "\n".join(result.alternatives[0].transcript for result in response.results)
    
    return transcribed_text

@click.command()
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('-o', '--output', default='transcribed_audio_text.txt', help='Path to save the extracted speech text from audio.')
@click.option('--bucket', required=True, help='GCS bucket name to upload the audio for transcription.')
def cli(audio_path, output, bucket):
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

    # Transcribe audio using Google Cloud Speech with GCS URI
    click.echo(f"Transcribing speech from audio: {audio_path}")
    preprocessed_audio = preprocess_audio(audio_path)
    gcs_uri = upload_to_gcs(bucket, preprocessed_audio, "audio_for_transcription.wav")
    spoken_text = transcribe_long_audio_google_cloud_gcs(gcs_uri, language_code="pl-PL")

    # Save the transcribed text to the specified output file
    with open(output, 'w') as f:
        f.write(spoken_text)
    
    click.echo(f"Transcription complete. Text saved to: {output}")

    # Optionally, remove the temporary extracted audio file
    if os.path.exists("extracted_audio.wav"):
        os.remove("extracted_audio.wav")


if __name__ == "__main__":
    cli()  # For running audio CLI directly