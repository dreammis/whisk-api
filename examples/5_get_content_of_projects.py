import asyncio
import os
from typing import List, Dict, Any # For type hinting
from src.index import Whisk, WhiskApiException
# Projects and ImageMetadata can be imported for type hinting context if needed,
# but the actual objects from Whisk client will be dicts.
from src.global_types import Credentials, Projects, ImageMetadata

async def main():
    """
    Example script to list content of a project using the Whisk client.
    It first fetches project history, then content of the first project found.
    """
    cookie = os.environ.get("COOKIE")
    if not cookie:
        print("Warning: COOKIE environment variable not set. Using placeholder.")
        print("Please set the COOKIE environment variable with your actual cookie value.")
        cookie = "INVALID_COOKIE"  # Placeholder

    credentials = Credentials(cookie=cookie)

    try:
        whisk_client = Whisk(credentials=credentials)

        print("Attempting to fetch project history (limit: 1)...")
        # project_history is List[Dict[str, Any]]
        project_history: List[Dict[str, Any]] = await whisk_client.get_project_history(limit=1)

        if not project_history:
            print("No projects found in history. Cannot fetch project content.")
            return

        first_project = project_history[0]
        project_id = first_project.get("name")
        project_title = first_project.get("displayName", "N/A")

        if not project_id:
            print("Could not determine Project ID from history. Cannot fetch project content.")
            return

        print(f"\nFetching content for Project ID: {project_id} (Title: {project_title})...")

        # project_content is List[Dict[str, Any]]
        project_content: List[Dict[str, Any]] = await whisk_client.get_project_content(project_id)

        if not project_content:
            print(f"No content found for project ID: {project_id}.")
            return

        print(f"\n--- Content of Project: {project_id} ---")
        for item in project_content:
            item_id = item.get("name") # This is usually the image ID or media key
            create_time = item.get("createTime")

            # ImageDetails are nested under 'image' key in ImageMetadata
            image_details = item.get("image", {})
            if not isinstance(image_details, dict): # Ensure image_details is a dict
                image_details = {}
            prompt = image_details.get("prompt", "N/A")

            print(f"  Image/Media ID: {item_id}")
            print(f"  Created At: {create_time}")
            print(f"  Prompt: {prompt}")
            print("  -------")

        print(f"\nSuccessfully fetched and displayed {len(project_content)} item(s) from project {project_id}.")

    except WhiskApiException as e:
        print(f"API Error: {e}")
        if e.underlying_error:
            print(f"Underlying error: {e.underlying_error}")
    except ValueError as e: # Catch potential ValueError from Whisk constructor
        print(f"Configuration error: {e}")
    except IndexError: # If project_history was unexpectedly empty after check (should not happen)
        print("Error: No projects found, cannot proceed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
