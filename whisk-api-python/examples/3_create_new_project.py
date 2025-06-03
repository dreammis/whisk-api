import os
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI # Updated import
from requests.exceptions import RequestException

def example_create_new_project():
    """
    Example demonstrating how to create a new project.
    """
    print("--- Example: Create New Project ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        project_title = "My Python Client Project"
        print(f"Attempting to create a new project with title: '{project_title}'...")

        # The create_project method returns the project ID string directly.
        project_id = whisk.create_project(title=project_title)

        if project_id:
            print("Successfully created new project.")
            print(f"New Project ID: {project_id}")
        else:
            # This path may not be hit if errors cause exceptions.
            print("Failed to create new project, no project ID returned.")

    except RequestException as e:
        print(f"API Request Error: Failed to create project. {e}")
    except ValueError as e:
        # This could be from parsing issues if the response isn't as expected
        print(f"Value Error: Could not process the response or input for project creation. {e}")
    except Exception as e:
        print(f"An unexpected error occurred during project creation: {e}")
    finally:
        print("--- Create New Project Example Finished ---")

if __name__ == "__main__":
    example_create_new_project()
