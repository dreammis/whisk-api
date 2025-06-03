import os
# import sys
import time

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, GenerateImageRequest, GenerateImageResponse # Updated import
from requests.exceptions import RequestException

def example_generate_and_save_image():
    """
    Example demonstrating how to generate an image and then save it to a file.
    """
    print("--- Example: Generate and Save Image ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        # 1. Generate an image
        prompt_text = f"A serene landscape at dusk with a calming atmosphere - {int(time.time())}"
        print(f"Attempting to generate an image with prompt: '{prompt_text}'...")

        image_request = GenerateImageRequest(
            prompt=prompt_text,
            image_model="IMAGEN_3", # Or any preferred model
            aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE" # Or any preferred aspect ratio
        )

        image_response: GenerateImageResponse = whisk.generate_image(request_data=image_request)

        if not (image_response and image_response.image_panels and \
                image_response.image_panels[0].generated_images and \
                image_response.image_panels[0].generated_images[0].encoded_image):
            print("Failed to generate image or image data not found in response.")
            return

        encoded_image_data = image_response.image_panels[0].generated_images[0].encoded_image
        print("Image generated successfully.")

        # 2. Save the generated image
        # Create a unique filename, e.g., using a timestamp
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.png"

        print(f"Attempting to save the generated image as '{filename}'...")
        save_success = whisk.save_image(encoded_image_data=encoded_image_data, filename=filename)

        if save_success:
            print(f"Image successfully saved as '{filename}'.")
            # Note: In a real application, you might want to clean up by deleting the saved file afterwards
            # if it's just for temporary use in the example.
            # For example: os.remove(filename)
        else:
            print(f"Failed to save the image to '{filename}'.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Generate and Save Image Example Finished ---")

if __name__ == "__main__":
    example_generate_and_save_image()
