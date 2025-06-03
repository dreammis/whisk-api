import os
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, ImageHistoryItem # Updated import
from requests.exceptions import RequestException
from typing import List

def example_get_image_history():
    """
    Example demonstrating how to fetch and list image generation history.
    """
    print("--- Example: Get Image Generation History ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        limit = 12  # As per the TS example
        print(f"Attempting to fetch image generation history (limit: {limit})...")

        image_history: List[ImageHistoryItem] = whisk.get_image_history(limit=limit)

        if image_history:
            print(f"Successfully fetched {len(image_history)} image history entries:")
            for image_item in image_history:
                print(f"  Image ID (Name): {image_item.name}")
                print(f"  Create Time:     {image_item.create_time}")
                if image_item.media and image_item.media.image:
                    print(f"  Prompt:          {image_item.media.image.prompt}")
                    print(f"  Model Used:      {image_item.media.image.model_name_type}")
                else:
                    print("  Media/Image Details: Not available")
                print("  -------")
        elif image_history == []: # Explicitly checking for an empty list
            print("Successfully fetched image history: No images found.")
        else:
            print("Failed to fetch image history.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Get Image Generation History Example Finished ---")

if __name__ == "__main__":
    example_get_image_history()
