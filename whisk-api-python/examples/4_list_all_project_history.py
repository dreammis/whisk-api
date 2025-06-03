import os
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI, ProjectHistoryItem # Updated import
from requests.exceptions import RequestException
from typing import List

def example_list_project_history():
    """
    Example demonstrating how to fetch and list project history.
    """
    print("--- Example: List Project History ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        limit = 12  # As per the TS example
        print(f"Attempting to fetch project history (limit: {limit})...")

        projects: List[ProjectHistoryItem] = whisk.get_project_history(limit=limit)

        if projects:
            print(f"Successfully fetched {len(projects)} projects:")
            for project in projects:
                print(f"  Project ID (Name): {project.name}")
                print(f"  Display Name:      {project.display_name}")
                print(f"  Create Time:       {project.create_time}")
                # The 'media' field is complex and not fully defined in ProjectHistoryItem
                # print(f"  Media:             {project.media}")
                print("  -------")
        elif projects == []: # Explicitly checking for an empty list, meaning success but no projects
            print("Successfully fetched project history: No projects found.")
        else:
            # This case might not be reached if errors cause exceptions or an empty list is returned.
            print("Failed to fetch project history, no projects returned.")

    except RequestException as e:
        print(f"API Request Error: Failed to fetch project history. {e}")
    except ValueError as e:
        print(f"Value Error: Could not process the response for project history. {e}")
    except Exception as e:
        print(f"An unexpected error occurred during project history fetching: {e}")
    finally:
        print("--- List Project History Example Finished ---")

if __name__ == "__main__":
    example_list_project_history()
