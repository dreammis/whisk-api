import pytest
import os
# sys path manipulation is no longer needed if tests are run with `python -m pytest` from root,
# or if the package is installed in editable mode (`pip install -e .`)
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI # Assuming WhiskAPI is exposed in whisk_api/__init__.py

@pytest.fixture(scope="session")
def api_client() -> WhiskAPI: # Keep type hint for clarity
    """
    Pytest fixture to provide an initialized WhiskAPI client.
    Reads the session cookie from the WHISK_SESSION_COOKIE environment variable.
    Skips tests if the cookie is not set.
    """
    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        pytest.skip("WHISK_SESSION_COOKIE environment variable not set. Skipping tests that require authentication.")

    try:
        client = WhiskAPI(session_cookie=session_cookie) # This should now work due to the package structure
        return client
    except ValueError as e: # Catch potential errors during client initialization (e.g., empty cookie string)
        pytest.fail(f"Failed to initialize WhiskAPI client: {e}")
    except Exception as e: # Catch any other import or init errors
        pytest.fail(f"Failed to initialize WhiskAPI client due to an unexpected error: {e}")


@pytest.fixture(scope="session")
def valid_cookie_is_set() -> bool:
    """
    Fixture to check if the cookie is set, for tests that don't need a client but depend on the cookie.
    """
    return bool(os.environ.get("WHISK_SESSION_COOKIE"))
