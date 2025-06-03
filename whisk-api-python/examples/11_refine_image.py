import os
# import sys
import time

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, GenerateImageRequest, RefineImageRequest, GenerateImageResponse # Updated import
from requests.exceptions import RequestException

def example_refine_image():
    """
    Example demonstrating how to generate an image and then refine it.
    Saves both the initial and the refined image.
    """
    print("--- Example: Refine Image ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        # 1. Generate an initial image
        timestamp = int(time.time())
        initial_prompt = f"A whimsical treehouse in a fantasy forest - {timestamp}"
        print(f"Attempting to generate initial image with prompt: '{initial_prompt}'...")

        gen_request = GenerateImageRequest(prompt=initial_prompt, image_model="IMAGEN_3")
        gen_response: GenerateImageResponse = whisk.generate_image(request_data=gen_request)

        if not (gen_response and gen_response.image_panels and \
                gen_response.image_panels[0].generated_images and \
                gen_response.image_panels[0].generated_images[0].encoded_image):
            print("Failed to generate initial image or image data not found.")
            return

        first_image_details = gen_response.image_panels[0].generated_images[0]
        initial_encoded_image = first_image_details.encoded_image
        initial_image_id = first_image_details.media_generation_id # This is the 'imageId' for refinement
        initial_prompt_from_response = first_image_details.prompt # Use the exact prompt from response

        print("Initial image generated successfully.")

        # Save the initial image
        initial_filename = f"refine_example_stage1_{timestamp}.png"
        if whisk.save_image(initial_encoded_image, initial_filename):
            print(f"Initial image saved as '{initial_filename}'.")
        else:
            print(f"Failed to save initial image as '{initial_filename}'.")

        # 2. Refine the generated image
        refinement_prompt = "Add a dragon flying around the treehouse, sunset lighting"
        print(f"Attempting to refine the image with: '{refinement_prompt}'...")

        refine_request = RefineImageRequest(
            existing_prompt=initial_prompt_from_response, # Use prompt from the generated image
            new_refinement=refinement_prompt,
            base64_image=initial_encoded_image,
            image_id=initial_image_id, # mediaGenerationId from the first image
            image_model=first_image_details.image_model or "IMAGEN_3" # Use model from first image or default
        )

        refined_response: GenerateImageResponse = whisk.refine_image(request_data=refine_request)

        if not (refined_response and refined_response.image_panels and \
                refined_response.image_panels[0].generated_images and \
                refined_response.image_panels[0].generated_images[0].encoded_image):
            print("Failed to refine image or refined image data not found.")
            return

        refined_encoded_image = refined_response.image_panels[0].generated_images[0].encoded_image
        print("Image refined successfully.")

        # Save the refined image
        refined_filename = f"refine_example_stage2_{timestamp}.png"
        if whisk.save_image(refined_encoded_image, refined_filename):
            print(f"Refined image saved as '{refined_filename}'.")
        else:
            print(f"Failed to save refined image as '{refined_filename}'.")

        print(f"Image refinement completed. Initial: '{initial_filename}', Refined: '{refined_filename}'.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Refine Image Example Finished ---")

if __name__ == "__main__":
    example_refine_image()
