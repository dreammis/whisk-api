import pytest
import time
# from whisk_api import WhiskAPI # Provided by fixture
from whisk_api.types import ProjectHistoryItem
from requests.exceptions import RequestException
from typing import List

@pytest.mark.api_call
def test_project_lifecycle(api_client): # Type hint :WhiskAPI
    """
    Tests the full lifecycle of a project:
    1. Create a new project.
    2. Get project history and verify the new project is listed (implicitly).
    3. Rename the project.
    4. Get project history and verify the renamed project (implicitly).
    5. Delete the project.
    6. Get project history and verify the project is no longer listed (implicitly).
    """
    timestamp = int(time.time())
    original_project_title = f"Test Project {timestamp}"
    renamed_project_title = f"Renamed Test Project {timestamp}"
    created_project_id = None # To store the ID of the project we create

    try:
        # 1. Create a new project
        print(f"Creating project with title: {original_project_title}")
        created_project_id = api_client.create_project(title=original_project_title)
        assert created_project_id is not None
        assert isinstance(created_project_id, str)
        assert len(created_project_id) > 0
        print(f"Project created successfully. Project ID: {created_project_id}")

        # 2. Get project history and verify creation (optional explicit check)
        # For brevity, we'll implicitly verify by checking if rename/delete targets this ID.
        # A full check would list history and find the project by ID or title.

        # 3. Rename the project
        print(f"Renaming project ID {created_project_id} to: {renamed_project_title}")
        # The rename_project method in the client currently returns the project ID string.
        # The TS client also expects the ID string as response.
        rename_response_id = api_client.rename_project(project_id=created_project_id, new_name=renamed_project_title)
        assert rename_response_id is not None
        assert rename_response_id == created_project_id # Usually, rename returns the same ID
        print(f"Project rename requested. Response ID: {rename_response_id}")

        # Verify rename by fetching the specific project (if such method existed) or by listing and finding.
        # For now, assume rename worked if no error. A robust test would re-fetch and check displayName.
        # Let's try to fetch history and see if we find the new name.
        time.sleep(2) # Allow some time for changes to propagate if the API is eventually consistent
        history_after_rename: List[ProjectHistoryItem] = api_client.get_project_history(limit=10)
        renamed_project_found = False
        for p_item in history_after_rename:
            if p_item.name == created_project_id: # name is the ID
                assert p_item.display_name == renamed_project_title
                renamed_project_found = True
                print(f"Verified renamed project in history: ID {p_item.name}, New Name: {p_item.display_name}")
                break
        assert renamed_project_found, f"Renamed project (ID: {created_project_id}, New Name: {renamed_project_title}) not found in history after rename attempt."


    except RequestException as e:
        pytest.fail(f"API request failed during project lifecycle test: {e}")
    except ValueError as e:
        pytest.fail(f"Value error (e.g., parsing response) during project lifecycle test: {e}")
    except AssertionError as e:
        pytest.fail(f"Assertion failed during project lifecycle test: {e}")
    except Exception as e: # Catch any other unexpected error
        if created_project_id: # Try to clean up even if a non-assertion error occurred mid-test
            print(f"An unexpected error occurred: {e}. Attempting cleanup of project {created_project_id}...")
        else:
            print(f"An unexpected error occurred: {e}.")
        pytest.fail(f"Unexpected exception: {e}")
    finally:
        # 5. Delete the project (ensure this runs even if assertions fail mid-test)
        if created_project_id:
            print(f"Cleaning up: Deleting project ID {created_project_id}")
            delete_success = api_client.delete_projects(project_ids=[created_project_id])
            assert delete_success, f"Failed to delete project ID {created_project_id} during cleanup."
            print(f"Project {created_project_id} deletion request successful.")

            # 6. Verify deletion by trying to fetch it or checking history (optional)
            time.sleep(2) # Allow time for deletion to propagate
            history_after_delete: List[ProjectHistoryItem] = api_client.get_project_history(limit=10)
            deleted_project_truly_gone = True
            for p_item_final in history_after_delete:
                if p_item_final.name == created_project_id:
                    deleted_project_truly_gone = False
                    print(f"Error: Deleted project {created_project_id} still found in history.")
                    break
            assert deleted_project_truly_gone, f"Project {created_project_id} was not properly deleted or still appears in history."
            print(f"Verified project {created_project_id} is no longer in recent history.")
        else:
            print("No project ID captured for cleanup.")

@pytest.mark.api_call
def test_get_project_history_limit(api_client): # Type hint :WhiskAPI
    """Tests get_project_history with a limit."""
    limit = 3
    print(f"Testing get_project_history with limit={limit}")
    try:
        projects = api_client.get_project_history(limit=limit)
        assert projects is not None
        assert isinstance(projects, list)
        # The number of projects returned can be less than the limit if there aren't enough.
        assert len(projects) <= limit, f"Expected number of projects to be <= {limit}, got {len(projects)}"
        print(f"Received {len(projects)} projects (limit was {limit}).")
        for project in projects:
            assert isinstance(project, ProjectHistoryItem)
            assert project.name and project.display_name and project.create_time
    except RequestException as e:
        pytest.fail(f"API request failed: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

# Note: More granular tests (e.g., test_create_project_only, test_rename_project_only)
# would require careful management of test data (e.g., creating a project in setup, deleting in teardown)
# or using unique names and hoping for eventual cleanup if direct deletion after each test isn't feasible.
# The lifecycle test above is more of an integration test for the project functionalities.
