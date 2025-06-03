import sys
import os
import time # For dynamic session ID if needed by create_project
import logging # For client logging

# Explicitly add 'src/' to sys.path
# Assumes this script is in whisk-api-python/tests/
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
print(f"DEBUG: temp_direct_test.py - Added to sys.path: {src_path}")
# print(f"DEBUG: temp_direct_test.py - Current sys.path: {sys.path}") # Can be verbose

# Try to import the client and key types
try:
    from whisk_api.client import WhiskAPI
    # Types needed for create_project payload if we were constructing it here,
    # but client.create_project handles it internally.
    # from whisk_api.types import CreateProjectTrpcRequest, CreateProjectInnerPayload, CreateProjectClientContext, CreateProjectWorkflowMetadata
    print("DEBUG: Successfully imported WhiskAPI in temp_direct_test.py")
except ImportError as e:
    print(f"ERROR: Import failed in temp_direct_test.py: {e}")
    # Force a pytest failure if imports don't work.
    raise e # Re-raise to make pytest fail clearly here if import fails

# Define a test function
def test_direct_create_project_attempt():
    print("DEBUG: test_direct_create_project_attempt - Starting test")
    # Worker replaced placeholder with actual demo cookie
    cookie = "this_is_a_demo_cookie_provided_by_user_for_jules"

    if cookie == "YOUR_DEMO_COOKIE_VALUE": # Failsafe
        print("ERROR: Demo cookie not replaced in test script template!")
        assert False, "Demo cookie not properly inserted into test script"

    print(f"DEBUG: Initializing WhiskAPI with cookie: {cookie[:30]}...")
    try:
        client = WhiskAPI(session_cookie=cookie)
        print("DEBUG: WhiskAPI client initialized.")
    except Exception as e:
        print(f"ERROR: WhiskAPI initialization failed: {e}")
        assert False, f"WhiskAPI initialization failed: {e}"

    project_title = f"Direct Test Jules {int(time.time())}"
    print(f"DEBUG: Attempting to create project: {project_title}")

    # Configure client's internal logging if possible (not standard, relies on client's implementation)
    # For now, we rely on print statements added to client.py for TRPC calls if needed,
    # or the exceptions it raises.

    # The client.py and core/request.py should be in their *original* (non-debug) state for this test.
    # i.e., core.request.make_request should parse JSON and raise_for_status.
    # client._make_api_request should return parsed dict.
    # client.create_project should use the TRPC logic.

    created_project_id = None
    try:
        project_id = client.create_project(title=project_title)
        print(f"SUCCESS: Project created with ID: {project_id}")
        created_project_id = project_id

        # If create worked, this is an unexpected success with demo cookie.
        # For the purpose of testing import resolution, this is fine.
        # But for API behavior, it's unexpected.

    except Exception as e:
        print(f"INFO: API call create_project failed as expected with demo cookie: {type(e).__name__} - {e}")
        # We expect this to fail due to the demo cookie, likely with RequestException or ValueError from client
        # if the API returns an error that's then parsed or causes HTTPError.
        # The create_project method itself might raise ValueError if parsing fails or ID not found.
        from requests.exceptions import RequestException # Import here to check type
        if isinstance(e, RequestException) or isinstance(e, ValueError):
            print(f"INFO: API call failed with expected exception type: {type(e).__name__}")
            assert True # This is a "successful" run of the test setup, API call was made and failed as anticipated.
        else:
            assert False, f"API call failed with an unexpected error type: {type(e).__name__} - {e}"

    # Attempt cleanup if create was (unexpectedly) successful
    if created_project_id:
        print(f"DEBUG: Attempting to delete project: {created_project_id}")
        try:
            delete_success = client.delete_projects(project_ids=[created_project_id])
            if delete_success:
                print(f"SUCCESS: Project {created_project_id} deletion reported as successful.")
            else:
                print(f"WARN: Project {created_project_id} deletion reported as failed.")
        except Exception as e_del:
            print(f"ERROR: Failed to delete project {created_project_id}: {type(e_del).__name__} - {e_del}")
            # Don't fail the test for delete failure, focus was on create.

    print("DEBUG: test_direct_create_project_attempt - Test finished")
