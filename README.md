# Image Processing Tools

This repository contains Python scripts for image processing and analysis using LLaVA and image organization.

## Requirements

- Python 3.x
- PIL (Python Imaging Library)
- requests (for LLaVA API interactions)
- Ollama with LLaVA model (for image analysis)

## Scripts

### 1. Image Renaming Tool (`rename_images.py`)

A utility script that processes JPG images and organizes them using MD5 hashes as filenames.

#### Features:
- Processes single JPG files or entire directories
- Calculates MD5 hash based on image content
- Creates an `images` directory to store processed files
- Preserves original files
- Handles image format conversion to RGB
- Includes error handling for corrupt or invalid images

#### Usage:
```bash
# Process a single image
python rename_images.py path/to/image.jpg

# Process all JPG images in a directory
python rename_images.py path/to/directory
```

### 2. LLaVA Image Analysis Tool (`main.py`)

A script that interfaces with Ollama's LLaVA model to analyze images and generate descriptions.

#### Features:
- Converts images to base64 format for API transmission
- Interfaces with Ollama's LLaVA model
- Supports custom prompts for image analysis
- Handles image format conversion
- Includes error handling for API requests

#### Usage:
```python
from main import query_llava

# Analyze an image
response = query_llava(
    image_path="path/to/image.jpg",
    prompt="What can you see in this image?"
)
print(response)
```

## Error Handling

Both scripts include comprehensive error handling for:
- Invalid file paths
- Corrupt images
- API connection issues
- Image format conversion problems

## Output Structure

- Renamed images are stored in an `images` directory
- Each image is renamed to its MD5 hash with a `.jpg` extension
- Original files remain unchanged in their original locations

## Notes

- The LLaVA analysis tool requires a running Ollama instance with the LLaVA model
- Only JPG images are supported for the renaming tool
- Images are converted to RGB format during processing
