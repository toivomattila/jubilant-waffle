import os
import hashlib
import shutil
from pathlib import Path
from PIL import Image
import io

def calculate_image_hash(image_path):
    """Calculate MD5 hash of an image file."""
    try:
        with Image.open(image_path) as img:
            # Convert image to RGB if it's not
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            # Calculate MD5 hash
            return hashlib.md5(img_bytes).hexdigest()
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def process_images(input_path):
    """Process images from input path and copy them to images folder with MD5 hash names."""
    # Create images directory if it doesn't exist
    output_dir = Path("images")
    output_dir.mkdir(exist_ok=True)
    
    input_path = Path(input_path)
    processed_files = []
    
    if input_path.is_file() and input_path.suffix.lower() == '.jpg':
        # Process single file
        files = [input_path]
    elif input_path.is_dir():
        # Process all jpg files in directory
        files = list(input_path.glob('**/*.jpg'))
    else:
        print(f"Invalid input path: {input_path}")
        return []
    
    for file_path in files:
        try:
            # Calculate hash
            file_hash = calculate_image_hash(file_path)
            if not file_hash:
                continue
                
            # Create new filename with hash
            new_filename = f"{file_hash}.jpg"
            output_path = output_dir / new_filename
            
            # Copy file to new location
            shutil.copy2(file_path, output_path)
            processed_files.append((file_path, output_path))
            print(f"Processed: {file_path} -> {output_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return processed_files

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python rename_images.py <path>")
        print("Path can be either a jpg image or a directory containing jpg images")
        sys.exit(1)
    
    input_path = sys.argv[1]
    processed_files = process_images(input_path)
    
    print(f"\nProcessed {len(processed_files)} images")
    print("All processed images are stored in the 'images' directory")

if __name__ == "__main__":
    main() 