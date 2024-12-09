# Image Tagging Application - Product Requirements Document

## Overview
The Image Tagging Application is a backend system designed to process, organize, and automatically tag images using AI-powered analysis. The system uses Ollama with the LLaVA model for generating image tags and implements a robust storage solution using both filesystem and database components.

## Core Features

### 1. Image Processing and Storage
- Process and store images using MD5 hash-based filenames
- Benefits of MD5 hash naming:
  - Prevents duplicate image storage by generating identical hashes for identical images
  - Enables efficient image deduplication
  - Creates a consistent and collision-resistant naming scheme
  - Facilitates easy image verification and integrity checking
  - Allows for distributed storage systems without naming conflicts
  - Eliminates issues with illegal filesystem characters from user-generated filenames
  - Ensures cross-platform compatibility by avoiding special characters

### 2. AI-Powered Image Analysis
- Integration with Ollama using the LLaVA model
- Automatic generation of descriptive tags for images
- Support for custom prompts to guide the AI analysis
- CLI support for repeated tagging:
  - Option to process the entire image set multiple times
  - Builds more accurate confidence metrics through repeated analysis
  - Helps identify consistently recognized features in images

### 3. Data Storage Requirements

The system must maintain persistent storage of the following information:

#### Image Data
- Unique identifier (MD5 hash) for each image
- Original filename for reference
- Timestamp of when the image was added
- Storage location of the processed image

#### Tag Data
- Association between images and their tags
- Storage of AI-generated tags for each image
- Support for multiple tags per image
- All tags must be stored in Title Case format (first letter of each word capitalized, rest lowercase)
- Tags can only contain letters and spaces (underscores should be converted to spaces)
- Track confidence metrics for each tag:
  - Number of times an image has been processed
  - Count of times each tag was generated for an image
  - Confidence percentage (tag occurrence count / total processing count)

#### Data Relationships
- Each image must be able to have multiple associated tags
- Tags must maintain their relationship with the source image
- Orphaned tags (tags without associated images) are fine

### 4. System Components
- Image processing module for handling file operations and MD5 hash generation
- LLaVA integration module for AI-powered image analysis
- Database management module for storing and retrieving image metadata and tags
- Error handling and logging system

## Technical Requirements

### Image Processing
- Support for JPG image format
- Automatic conversion to RGB format
- Preservation of original files
- Creation of organized image storage directory

### AI Integration
- Real-time image analysis using LLaVA model
- Configurable prompts for tag generation
- Error handling for API failures
- Timeout mechanism for image processing to handle model hangs
  - Skip images that exceed the processing timeout
  - Continue with the next image in queue when timeout occurs
- Support for configurable confidence thresholds:
  - User-definable minimum confidence level for tag inclusion
  - Allow multiple tagging runs on the same image to build confidence metrics
- CLI support for repeated tagging:
  - Option to process the entire image set multiple times
  - Builds more accurate confidence metrics through repeated analysis
  - Helps identify consistently recognized features in images

### Database
- SQLite for persistent storage
- Support for image metadata storage
- Efficient tag storage and retrieval
- Relationship mapping between images and their tags

## Performance Requirements
- Fast image processing and hash generation
- Efficient database queries
- Scalable storage solution
- Minimal duplicate image storage

## Security Requirements
- Secure storage of image files
- Protection against SQL injection
- Proper error handling and logging
- Data integrity verification
