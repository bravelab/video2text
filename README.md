
# Video Text Extractor

**Video Text Extractor** is a Python package that extracts text from video frames using OpenCV and Tesseract OCR. This package allows you to process video files frame by frame, extract the text content, and return it for further analysis.

## Features

- Extract text from video frames using Tesseract OCR
- Process videos frame by frame
- Simple interface to access the extracted text

## Requirements

- Python 3.8+
- OpenCV
- Pytesseract
- Tesseract-OCR (external dependency)

## Installation

First, install **Tesseract-OCR**:

- On Linux:
  ```bash
  sudo apt-get install tesseract-ocr
  ```
  
- On macOS:
  ```bash
  brew install tesseract
  ```

- On Windows, download the installer from [Tesseract OCR GitHub](https://github.com/tesseract-ocr/tesseract/wiki).

Then, you can install the package dependencies using Poetry:

```bash
poetry install
```

## Usage

Here is a simple example to extract text from a video:

```python
from video_text_extractor import VideoTextExtractor

# Create an instance of the extractor
extractor = VideoTextExtractor("path_to_your_video.mp4")

# Extract text from the video
text = extractor.extract_text()

# Print the extracted text
print(text)
```

## Testing

To run the tests, use:

```bash
poetry run pytest
```

## License

This project is licensed under the MIT License.# video2text
