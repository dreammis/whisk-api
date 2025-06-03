import os
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, ProjectHistoryItem # Updated import
from requests.exceptions import RequestException
from typing import List
import json # For pretty printing the media dictionary

def example_get_project_content():
    """
    Example demonstrating how to fetch project history and inspect basic 'media' content.
    Note: The 'media' field can be complex. This example prints it as a dictionary.
    "Content" of a project can be interpreted in many ways (e.g., associated images).
    This example shows the metadata available directly within the ProjectHistoryItem.
    """
    print("--- Example: Get Content of Projects (Metadata) ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        limit = 5 # Fetch a few projects for demonstration
        print(f"Attempting to fetch project history (limit: {limit}) to inspect their 'media' content...")

        projects: List[ProjectHistoryItem] = whisk.get_project_history(limit=limit)

        if projects:
            print(f"Successfully fetched {len(projects)} projects:")
            for project in projects:
                print(f"  Project ID (Name): {project.name}")
                print(f"  Display Name:      {project.display_name}")
                print(f"  Create Time:       {project.create_time}")
                if project.media:
                    print(f"  Media (raw dict):  {json.dumps(project.media, indent=2)}")
                else:
                    print("  Media:             Not available or None")
                print("  -------")

            print("\nNote on 'Project Content':")
            print("The 'media' dictionary above contains metadata associated with the project.")
            print("If 'content' refers to specific images within a project, you might need to:")
            print("1. Use 'get_image_history' and filter images by a project ID (if the API supports this).")
            print("2. Or, if a project ID is available in 'media' or 'name', use that with other API calls.")
            print("The current client and this example primarily show project-level metadata.")

        elif projects == []:
            print("Successfully fetched project history: No projects found.")
        else:
            print("Failed to fetch project history.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Get Content of Projects Example Finished ---")

if __name__ == "__main__":
    example_get_project_content()
