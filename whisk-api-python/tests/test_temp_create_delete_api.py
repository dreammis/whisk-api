import pytest
import time
import json # For printing dicts if needed, though client logs now
from whisk_api import WhiskAPI # For type hinting api_client
from requests.exceptions import RequestException

# This test assumes:
# 1. conftest.py's api_client fixture is providing a WhiskAPI instance
#    initialized with a (potentially simulated for this test) session cookie.
# 2. client.py's create_project and delete_projects methods, and their helpers
#    (_make_api_request, core.request.make_request) are temporarily modified
#    to log raw response details and handle raw requests.Response objects internally.

@pytest.mark.api_call # Mark as API call so it uses the api_client fixture
def test_temp_create_and_delete_project_with_new_url_logic(api_client: WhiskAPI):
    """
    Temporarily tests the corrected create_project (new URL, payload, parsing)
    and corrected delete_projects, expecting raw response details to be logged
    from within the client methods.
    """
    timestamp = int(time.time())
    create_project_title = f"Test Jules TRPC {timestamp}"

    print(f"\n--- Test: Corrected Create & Delete ---")
    print(f"Using Project Title: {create_project_title}")

    created_project_id = None # This should be the workflowId

    # --- Test Create Project (Corrected) ---
    print("\n--- Testing client.create_project (Corrected) ---")
    try:
        print(f"Calling client.create_project with title: '{create_project_title}'")
        # create_project is already modified to use new URL, payload, and log raw details
        created_project_id = api_client.create_project(title=create_project_title)

        print(f"\nSUCCESS (test script): client.create_project returned Project ID (workflowId): {created_project_id}")
        assert created_project_id is not None
        assert isinstance(created_project_id, str)

    except RequestException as e:
        print(f"API Request Exception from client.create_project (test script): {e}")
        # Raw response details should have been logged from within client.py
    except ValueError as e:
        print(f"Value Error from client.create_project (test script): {e}")
    except Exception as e:
        print(f"An unexpected error occurred in client.create_project (test script): {type(e).__name__} - {e}")
        pytest.fail(f"Unexpected exception during create_project: {e}")


    # --- Test Delete Project (Corrected, if created) ---
    if created_project_id:
        print("\n--- Testing client.delete_projects (Corrected) ---")
        project_id_to_delete = created_project_id
        print(f"Attempting to delete project ID (workflowId): {project_id_to_delete}")

        delete_success = False
        try:
            # delete_projects is already modified to log raw details
            delete_success = api_client.delete_projects(project_ids=[project_id_to_delete])
            if delete_success:
                print(f"SUCCESS (test script): client.delete_projects reported success for ID: {project_id_to_delete}")
            else:
                # This will be a soft fail, error details should be in client logs
                print(f"FAILURE (test script): client.delete_projects reported failure for ID: {project_id_to_delete}")
            assert delete_success, "delete_projects returned False" # Make it a hard pytest fail if not success
        except RequestException as e:
            print(f"API Request Exception from client.delete_projects (test script): {e}")
        except ValueError as e:
            print(f"Value Error from client.delete_projects (test script): {e}")
        except Exception as e:
            print(f"An unexpected error occurred in client.delete_projects (test script): {type(e).__name__} - {e}")
            pytest.fail(f"Unexpected exception during delete_projects: {e}")
    else:
        print("\nSkipping delete_projects test as project creation failed or returned no ID.")

    print("\n--- Temporary Test Finished ---")
