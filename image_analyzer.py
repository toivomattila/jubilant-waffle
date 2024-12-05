import requests
import logging
from typing import List, Optional
from PIL import Image
import io
import json
import re

class ImageAnalyzer:
    """Class responsible for AI-powered image analysis using Ollama with LLaVA model."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", log_level: int = logging.WARNING):
        """Initialize the ImageAnalyzer with Ollama host configuration."""
        self.ollama_host = ollama_host
        self.model = "llava"
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)

    def _prepare_image(self, image_path: str) -> Image.Image:
        """
        Prepare the image for analysis by converting to RGB if necessary.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL.Image: Processed image in RGB format
        """
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            self.logger.error(f"Error preparing image: {str(e)}")
            raise

    def _encode_image_base64(self, image: Image.Image) -> str:
        """
        Encode the image to base64 format for API transmission.
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Base64 encoded image string
        """
        import base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _extract_json_from_text(self, text: str) -> List[dict]:
        """
        Extract JSON objects from text
        
        Assume that the response contains a JSON object but also additional unnecessary text.
        Parse the JSON object directly from the cleaned text.
        Then convert it to a dictionary and check if it has a "tags" key.
        If it does, add it to the list of JSON objects.
        
        Expected format: { "tags": ["tag1", "tag2", "tag3"] }
        
        Args:
            text: String that may contain JSON objects
            
        Returns:
            List[dict]: List of parsed JSON objects
        """
        json_objects = []
        # Find all potential JSON objects using regex
        json_pattern = r'\{[\s\S]*?\}'  # Modified pattern to include newlines
        matches = re.finditer(json_pattern, text)
        
        for match in matches:
            try:
                # Clean up the matched text by removing escape characters
                json_str = match.group().strip()
                if '\\n' in json_str:  # If string contains escaped newlines
                    json_str = json_str.encode().decode('unicode-escape')
                # Try to parse the matched text as JSON
                json_obj = json.loads(json_str)
                # Validate that it has a 'tags' key and it's a list
                if isinstance(json_obj.get('tags'), list):
                    json_objects.append(json_obj)
            except json.JSONDecodeError as e:
                self.logger.warning(f"Error parsing JSON: {str(e)}")
                self.logger.warning(f"Failed JSON: {match.group()}")
                continue
        
        return json_objects

    def analyze_image(self, image_path: str, custom_prompt: Optional[str] = None) -> List[str]:
        """
        Analyze an image using the LLaVA model and return generated tags.

        Example response:
        {"model":"llava","created_at":"2024-12-05T06:43:59.021312552Z","response":" ```json\n{\n    \"tags\": [\"tag1\", \"tag2\", \"tag3\"]\n}\n```"}
        
        Args:
            image_path: Path to the image file
            custom_prompt: Optional custom prompt to guide the analysis
            
        Returns:
            List[str]: List of generated tags
        """
        try:
            # Prepare the image
            image = self._prepare_image(image_path)
            base64_image = self._encode_image_base64(image)

            # Prepare the prompt
            if not custom_prompt:
                custom_prompt = """Analyze this image and return an extensive list of tags in JSON format.
The tags are used for image search, filtering, and organizing application.
The tags should be as diverse as possible.
The more tags the better.
The more detailed tags the better.
Example response format: { "tags": ["tag1", "tag2", "tag3"] }

Return only the JSON object without any additional text."""

            # Prepare the API request
            api_url = f"{self.ollama_host}/api/generate"
            payload = {
                "model": self.model,
                "prompt": custom_prompt,
                "images": [base64_image],
                "stream": False
            }

            # Make the API request
            response = requests.post(api_url, json=payload, timeout=5)
            response.raise_for_status()

            # Process the response
            # First read the response text to JSON
            response_json = json.loads(response.text)
            # Then extract the response text from the JSON
            response_text = response_json.get("response")  # For now throw an error if it's missing
            
            # Extract JSON objects from response
            json_objects = self._extract_json_from_text(response_text)
            
            # Collect all tags from all valid JSON responses
            all_tags = set()
            for json_obj in json_objects:
                # Add direct tags if they exist
                if isinstance(json_obj.get('tags'), list):
                    all_tags.update(json_obj['tags'])
            
            tags = list(all_tags)
            # Convert underscores to spaces and title case
            tags = [tag.replace('_', ' ') for tag in tags]
            # Convert to title case
            tags = [tag.title() for tag in tags]
            self.logger.info(f"Generated {len(tags)} tags for image: {image_path}")
            return tags

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            raise

    def is_model_available(self) -> bool:
        """
        Check if the LLaVA model is available and running in Ollama.
        
        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_host}/api/tags")
            response.raise_for_status()
            available_models = response.json().get('models', [])
            return any(model.get('name') == self.model for model in available_models)
        except:
            return False 

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze an image and generate tags using LLaVA model.')
    parser.add_argument('image_path', help='Path to the image file to analyze')
    args = parser.parse_args()
    
    analyzer = ImageAnalyzer()
    try:
        tags = analyzer.analyze_image(args.image_path)
        # print("\nGenerated tags:")
        for tag in tags:
            # print(f"- {tag}")
            print(tag)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1) 