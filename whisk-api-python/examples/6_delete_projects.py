import os
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, ProjectHistoryItem # Updated import
from requests.exceptions import RequestException
from typing import List

def example_delete_projects():
    """
    Example demonstrating how to delete projects.
    It first fetches project history, then attempts to delete the first project found.
    """
    print("--- Example: Delete Projects ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        # 1. Fetch project history to find a project to delete
        print("Attempting to fetch project history to find a project to delete...")
        projects: List[ProjectHistoryItem] = whisk.get_project_history(limit=5)

        if not projects:
            print("No projects found in history. Cannot demonstrate deletion.")
            # To test deletion, you might want to create a project first.
            # For example:
            # try:
            #     temp_project_id = whisk.create_project("Temporary Project for Deletion Test")
            #     print(f"Created temporary project: {temp_project_id}")
            #     projects_to_delete = [temp_project_id]
            # except Exception as create_err:
            #     print(f"Failed to create a temporary project for deletion test: {create_err}")
            #     return
            return

        # 2. Select project(s) to delete
        # The TS example deletes the first project. We'll do the same.
        # ProjectHistoryItem.name is the project ID.
        project_to_delete_id = projects[0].name
        print(f"Found project '{projects[0].display_name}' (ID: {project_to_delete_id}). Attempting to delete it.")

        # 3. Delete the project
        # The delete_projects method takes a list of project IDs.
        success = whisk.delete_projects(project_ids=[project_to_delete_id])

        if success:
            print(f"Successfully sent delete request for project ID: {project_to_delete_id}.")
            print("Note: The API might return success even if the project was already deleted or did not exist.")
            print("Verify deletion by trying to fetch its history again or via the Web UI.")
        else:
            print(f"Failed to delete project ID: {project_to_delete_id}.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Delete Projects Example Finished ---")

if __name__ == "__main__":
    example_delete_projects()
