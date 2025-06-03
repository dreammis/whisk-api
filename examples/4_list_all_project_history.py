import asyncio
import os
from typing import List, Dict, Any # For type hinting the project list
from src.index import Whisk, WhiskApiException
from src.global_types import Credentials, Projects # Projects can be used for type hint if objects were instantiated

async def main():
    """
    Example script to list project history using the Whisk client.
    """
    cookie = os.environ.get("COOKIE")
    if not cookie:
        print("Warning: COOKIE environment variable not set. Using placeholder.")
        print("Please set the COOKIE environment variable with your actual cookie value.")
        cookie = "INVALID_COOKIE"  # Placeholder

    credentials = Credentials(cookie=cookie)
    limit = 12  # Example limit

    try:
        whisk_client = Whisk(credentials=credentials)

        print(f"Attempting to fetch project history (limit: {limit})...")
        # project_history is List[Projects], but Projects are dicts from JSON
        project_history: List[Dict[str, Any]] = await whisk_client.get_project_history(limit)

        if not project_history:
            print("No project history found or an empty list was returned.")
            return

        print("\n--- Project History ---")
        for project in project_history:
            # The `get_project_history` method in Whisk.py uses `cast(List[Projects], workflow_list)`
            # but `workflow_list` is the direct JSON parsed list of dicts.
            # So, we access items as dictionary keys.
            project_id = project.get("name")
            project_title = project.get("displayName")

            print(f"Project ID: {project_id}")
            print(f"Project Title: {project_title}")
            # Example to show media if available (structure based on Projects dataclass)
            # media = project.get("media")
            # if media and isinstance(media, dict):
            #     print(f"  Media Name: {media.get('name')}")
            #     image_info = media.get("image")
            #     if image_info and isinstance(image_info, dict):
            #         print(f"    Image Prompt: {image_info.get('prompt')}")
            print("------- x --------\n")

        print(f"Successfully fetched and displayed {len(project_history)} project(s).")

    except WhiskApiException as e:
        print(f"Error fetching project history: {e}")
        if e.underlying_error:
            print(f"Underlying error: {e.underlying_error}")
    except ValueError as e: # Catch potential ValueError from Whisk constructor
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
