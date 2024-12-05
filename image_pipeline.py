import os
import logging
from typing import List, Optional
from pathlib import Path
from image_analyzer import ImageAnalyzer
from db_manager import DatabaseManager

class ImagePipeline:
    """Pipeline for processing images and storing their tags."""
    
    def __init__(self, image_dir: str = "images"):
        """
        Initialize the image processing pipeline.
        
        Args:
            image_dir: Directory containing images
        """
        self.image_dir = Path(image_dir)
        self.analyzer = ImageAnalyzer()
        self.db = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # Create directory if it doesn't exist
        self.image_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def get_hash_from_filename(self, image_path: Path) -> str:
        """Extract MD5 hash from filename."""
        return image_path.stem  # Return filename without extension

    def process_image(self, image_path: Path) -> Optional[int]:
        """
        Process a single image and store its tags.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Optional[int]: Image ID if successful, None if failed
        """
        try:
            # Get MD5 hash from filename
            md5_hash = self.get_hash_from_filename(image_path)
            
            # Check if image already processed
            existing_image = self.db.get_image_by_hash(md5_hash)
            if existing_image:
                self.logger.info(f"Image already processed: {image_path.name}")
                return existing_image["id"]
            
            # Add image to database
            image_id = self.db.add_image(
                str(image_path),
                md5_hash,
                image_path.name
            )
            
            # Generate tags
            tags_data = self.analyzer.analyze_image(str(image_path))
            
            # Store tags in database
            self.db.add_tags(image_id, tags_data)
            
            self.logger.info(f"Successfully processed image: {image_path.name}")
            return image_id
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path.name}: {str(e)}")
            return None

    def process_directory(self) -> List[int]:
        """
        Process all images in the input directory.
        
        Returns:
            List[int]: List of successfully processed image IDs
        """
        processed_ids = []
        
        # Get all jpg files
        image_files = list(self.image_dir.glob("*.jpg")) + list(self.image_dir.glob("*.jpeg"))
        
        for image_path in image_files:
            image_id = self.process_image(image_path)
            if image_id is not None:
                processed_ids.append(image_id)
        
        self.logger.info(f"Processed {len(processed_ids)} images successfully")
        return processed_ids

def main():
    """Main entry point for the image processing pipeline."""
    pipeline = ImagePipeline()
    pipeline.process_directory()

if __name__ == "__main__":
    main() 