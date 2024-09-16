import pytest
import os
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from video2text import video_cli, audio_cli


@pytest.fixture
def mock_video_file(tmp_path):
    """Create a mock video file."""
    video_file = tmp_path / "test_video.mp4"
    video_file.write_text("dummy content")  # Create a dummy file
    return str(video_file)


@pytest.fixture
def mock_audio_file(tmp_path):
    """Create a mock audio file."""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.write_text("dummy content")  # Create a dummy file
    return str(audio_file)


@patch('video2text.VideoFileClip')
@patch('speech_recognition.Recognizer')  # Correct patch for speech_recognition
def test_video_cli(mock_recognizer, mock_videoclip, mock_video_file, tmp_path):
    # Mock video clip object
    mock_video = MagicMock()
    mock_video.audio.write_audiofile.return_value = None  # Mock writing audio file
    mock_videoclip.return_value = mock_video  # Return mock video object

    # Mock recognizer behavior
    mock_recognizer_instance = MagicMock()
    mock_recognizer.return_value = mock_recognizer_instance
    mock_recognizer_instance.recognize_google.return_value = "Test transcription"

    # Output file path
    output_file = tmp_path / "output.txt"

    # Use CliRunner to test Click command
    runner = CliRunner()
    result = runner.invoke(video_cli, [mock_video_file, '-o', str(output_file)])

    # Assertions
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, 'r') as f:
        assert f.read() == "Test transcription"


@patch('speech_recognition.Recognizer')  # Correct patch for speech_recognition
def test_audio_cli(mock_recognizer, mock_audio_file, tmp_path):
    # Mock recognizer behavior
    mock_recognizer_instance = MagicMock()
    mock_recognizer.return_value = mock_recognizer_instance
    mock_recognizer_instance.recognize_google.return_value = "Test transcription"

    # Output file path
    output_file = tmp_path / "output.txt"

    # Use CliRunner to test Click command
    runner = CliRunner()
    result = runner.invoke(audio_cli, [mock_audio_file, '-o', str(output_file)])

    # Assertions
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, 'r') as f:
        assert f.read() == "Test transcription"


@patch('video2text.extract_audio_from_video')
@patch('speech_recognition.Recognizer')  # Correct patch for speech_recognition
def test_audio_cli_with_video(mock_recognizer, mock_extract_audio, mock_video_file, tmp_path):
    # Mock audio extraction from video
    mock_extract_audio.return_value = None  # Mock that audio was extracted

    # Mock recognizer behavior
    mock_recognizer_instance = MagicMock()
    mock_recognizer.return_value = mock_recognizer_instance
    mock_recognizer_instance.recognize_google.return_value = "Test transcription from video"

    # Output file path
    output_file = tmp_path / "output.txt"

    # Use CliRunner to test Click command
    runner = CliRunner()
    result = runner.invoke(audio_cli, [mock_video_file, '-o', str(output_file)])

    # Assertions
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, 'r') as f:
        assert f.read() == "Test transcription from video"