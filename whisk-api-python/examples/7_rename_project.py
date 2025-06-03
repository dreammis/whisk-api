import os
# import sys
import time

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, ProjectHistoryItem # Updated import
from requests.exceptions import RequestException
from typing import List

def example_rename_project():
    """
    Example demonstrating how to rename a project.
    It first fetches project history, then attempts to rename the first project found.
    """
    print("--- Example: Rename Project ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        # 1. Fetch project history to find a project to rename
        print("Attempting to fetch project history to find a project to rename...")
        projects: List[ProjectHistoryItem] = whisk.get_project_history(limit=5)

        if not projects:
            print("No projects found in history. Cannot demonstrate rename.")
            # Optionally, create a project here to ensure one exists for testing rename
            # try:
            #     project_id_to_rename = whisk.create_project("Project To Be Renamed")
            #     print(f"Created temporary project {project_id_to_rename} for renaming.")
            # except Exception as create_err:
            #     print(f"Could not create temporary project: {create_err}")
            #     return
            return

        project_to_rename = projects[0]
        project_id_to_rename = project_to_rename.name
        original_name = project_to_rename.display_name

        print(f"Found project '{original_name}' (ID: {project_id_to_rename}).")

        # 2. Define new name and rename
        new_name = f"Renamed Project ({int(time.time())})" # Add timestamp to ensure uniqueness
        print(f"Attempting to rename it to: '{new_name}'...")

        # The rename_project method returns the project ID (usually the same)
        renamed_project_id_response = whisk.rename_project(project_id=project_id_to_rename, new_name=new_name)

        if renamed_project_id_response:
            print("Successfully sent rename request.")
            print(f"Response Project ID: {renamed_project_id_response}")
            if renamed_project_id_response == project_id_to_rename:
                print(f"Project '{original_name}' (ID: {project_id_to_rename}) should now be named '{new_name}'.")
            else:
                print(f"Note: The API returned a different project ID ({renamed_project_id_response}) after renaming.")
            print("Verify the change by fetching project history again or via the Web UI.")
        else:
            # This path might not be hit if errors cause exceptions.
            print(f"Failed to rename project ID: {project_id_to_rename}.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Rename Project Example Finished ---")

if __name__ == "__main__":
    example_rename_project()
