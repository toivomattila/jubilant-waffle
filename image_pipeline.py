import os
import logging
from typing import List, Optional
from pathlib import Path

from tqdm import tqdm

from image_analyzer import ImageAnalyzer
from db_manager import DatabaseManager

class ImagePipeline:
    """Pipeline for processing images and storing their tags."""
    
    def __init__(self, image_dir: str = "images", log_level: int = logging.WARNING):
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
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def get_hash_from_filename(self, image_path: Path) -> str:
        """Extract MD5 hash from filename."""
        return image_path.stem  # Return filename without extension

    def process_image(self, image_path: Path) -> Optional[int]:
        """
        Process a single image and store its tags.
        The same image can be processed multiple times to build confidence metrics.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Optional[int]: Image ID if successful, None if failed
        """
        try:
            # Get MD5 hash from filename
            md5_hash = self.get_hash_from_filename(image_path)
            
            # Get or create image record
            existing_image = self.db.get_image_by_hash(md5_hash)
            if existing_image:
                image_id = existing_image["id"]
                self.logger.info(f"Processing existing image again: {image_path.name}")
            else:
                # Add new image to database
                image_id = self.db.add_image(
                    str(image_path),
                    md5_hash,
                    image_path.name
                )
                self.logger.info(f"Added new image to database: {image_path.name}")
            
            # Generate tags
            tags_data = self.analyzer.analyze_image(str(image_path))
            
            # Store tags in database (this will now update confidence metrics)
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
        
        for image_path in tqdm(image_files, desc="Processing images", unit="image"):
            image_id = self.process_image(image_path)
            if image_id is not None:
                processed_ids.append(image_id)
        
        self.logger.info(f"Processed {len(processed_ids)} images successfully")
        return processed_ids

def main():
    """Main entry point for the image processing pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process images and generate tags using LLaVA model.')
    parser.add_argument('--repeat', type=int, default=1, help='Number of times to repeat the tagging process (default: 1)')
    args = parser.parse_args()
    
    pipeline = ImagePipeline()
    for i in range(args.repeat):
        print(f"\nProcessing round {i + 1} of {args.repeat}")
        pipeline.process_directory()

if __name__ == "__main__":
    main() 