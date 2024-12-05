import requests
import base64
from PIL import Image
import io

def encode_image_to_base64(image_path):
    """
    Encode an image file to base64 string.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        str: Base64 encoded string of the image
    """
    with Image.open(image_path) as img:
        # Convert image to RGB if it's not
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Encode to base64
        base64_encoded = base64.b64encode(img_byte_arr).decode('utf-8')
        return base64_encoded

def query_llava(image_path, prompt, model="llava", api_url="http://localhost:11434/api/generate"):
    """
    Send an image to Ollama running LLava model and get the response.
    
    Args:
        image_path (str): Path to the image file
        prompt (str): Text prompt to send along with the image
        model (str): Name of the model to use (default: "llava")
        api_url (str): URL of the Ollama API
    
    Returns:
        str: Combined response from the model
    """
    # Encode the image
    base64_image = encode_image_to_base64(image_path)
    
    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [base64_image],
        "stream": False
    }
    
    try:
        # Send the request
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        # Parse and return the response
        return response.json()['response']
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making the request: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing response: {e}")
        return None

def main():
    # Example usage
    image_path = "./test.jpg"
    prompt = "What can you see in this image?"
    
    # Make sure Ollama is running and LLava model is pulled
    response = query_llava(image_path, prompt)
    
    if response:
        print("Model Response:")
        print(response)
    else:
        print("Failed to get response from the model")

if __name__ == "__main__":
    main()