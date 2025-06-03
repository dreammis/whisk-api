import os
# import sys
import time

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, GenerateImageRequest, GenerateImageResponse # Updated import
from requests.exceptions import RequestException

def example_generate_image():
    """
    Example demonstrating how to generate an image using the Whisk API.
    It shows how to make the request and access the encoded image data.
    Optionally, it also saves the image.
    """
    print("--- Example: Generate Image ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        # Define the image generation request
        # Using a unique prompt with a timestamp to avoid caching if any
        prompt_text = f"A vibrant abstract painting representing creativity - {int(time.time())}"
        print(f"Attempting to generate an image with prompt: '{prompt_text}'...")

        image_request = GenerateImageRequest(
            prompt=prompt_text,
            # Optional parameters (can be omitted to use API defaults)
            # image_model="IMAGEN_3",
            # aspect_ratio="IMAGE_ASPECT_RATIO_SQUARE",
            # seed=12345
        )

        image_response: GenerateImageResponse = whisk.generate_image(request_data=image_request)

        if image_response and image_response.image_panels:
            print("Image generation request successful.")
            # Iterate through panels and images (usually one panel, one image for basic prompts)
            for i, panel in enumerate(image_response.image_panels):
                print(f"  Image Panel {i+1}:")
                print(f"    Prompt used: {panel.prompt}")
                for j, img in enumerate(panel.generated_images):
                    print(f"    Generated Image {j+1}:")
                    print(f"      Seed: {img.seed}")
                    print(f"      Media Generation ID: {img.media_generation_id}")
                    print(f"      Encoded Image Data (first 50 chars): {img.encoded_image[:50]}...")

                    # The TS example saves the first image. We can do the same here.
                    if i == 0 and j == 0 and img.encoded_image:
                        filename = f"example_10_generated_image_{int(time.time())}.png"
                        print(f"      Attempting to save this image as '{filename}'...")
                        save_success = whisk.save_image(img.encoded_image, filename)
                        if save_success:
                            print(f"      Image saved as '{filename}'.")
                        else:
                            print(f"      Failed to save image as '{filename}'.")
        else:
            print("Failed to generate image or no image data returned in the expected structure.")

    except RequestException as e:
        print(f"API Request Error during image generation: {e}")
    except ValueError as e:
        print(f"Value Error (e.g., parsing response) during image generation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during image generation: {e}")
    finally:
        print("--- Generate Image Example Finished ---")

if __name__ == "__main__":
    example_generate_image()
