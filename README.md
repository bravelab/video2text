
# Audio/Video to Text Extractor with Google Cloud Speech-to-Text

This Python script extracts speech from audio or video files using **Google Cloud Speech-to-Text** and stores the transcribed text in a file. It automatically handles uploading long audio files to **Google Cloud Storage (GCS)** and processes both short and long audio files using Google Cloud's transcription APIs.

## Features

- Extract speech from both audio and video files (MP4, MKV, MOV, AVI).
- Converts audio to the required format (16kHz, 16-bit mono PCM WAV).
- Automatically uploads long audio files to Google Cloud Storage (GCS) for transcription.
- Uses Google Cloud Speech-to-Text for transcribing speech from audio/video.
- CLI-based usage for easy audio/video file processing.

## Requirements

- **Python 3.12+**
- **FFmpeg** (for audio extraction and conversion)
- **Google Cloud Speech-to-Text API** and **Google Cloud Storage**
- Google Cloud Credentials (Service Account JSON)

### Google Cloud Setup

1. Enable the **Google Cloud Speech-to-Text API** in the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a **Google Cloud Storage** bucket to upload audio files for transcription.
3. Set up a service account with appropriate permissions and download the service account JSON key file.
4. Set the environment variable for Google Cloud credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
   ```

### Installation

First, ensure **FFmpeg** is installed:

- On **Linux**:
  ```bash
  sudo apt-get install ffmpeg
  ```
- On **macOS**:
  ```bash
  brew install ffmpeg
  ```
- On **Windows**, download the installer from the [FFmpeg website](https://ffmpeg.org/download.html).

Install the required dependencies:

```bash
poetry install
```

### Usage

You can run the script to extract speech from an audio or video file and save the transcribed text to a file.

#### Command-Line Interface (CLI) Example:

```bash
poetry run audi input_file/video_file.mpg -o output_text.txt --bucket your_gcs_bucket
```

- `audio_path_to_audio_or_video_file`: The path to the audio or video file you want to transcribe.
- `output_text.txt`: The output file where the transcribed text will be saved.
- `your_gcs_bucket`: The Google Cloud Storage bucket where the audio file will be uploaded for transcription.

### License

This project is licensed under the MIT License.
