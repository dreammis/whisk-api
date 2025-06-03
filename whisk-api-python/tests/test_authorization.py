import pytest
# WhiskAPI is imported via the fixture from conftest, direct import not strictly needed here for the type hint
# from whisk_api import WhiskAPI
from requests.exceptions import RequestException

# Assuming conftest.py correctly provides WhiskAPI instance as api_client
# and that WhiskAPI type hint is understood by type checker via conftest or by installing the package.

@pytest.mark.api_call # Custom marker for tests making actual API calls
def test_get_authorization_token(api_client): # Type hint can be ': WhiskAPI' if setup allows mypy to find it
    """
    Tests if the get_authorization_token method returns a non-empty string.
    This implicitly tests if the authentication via session cookie is working.
    """
    print("Attempting to fetch authorization token...")
    try:
        # api_client is an instance of WhiskAPI from conftest.py
        token = api_client.get_authorization_token()
        assert token is not None, "Authorization token should not be None."
        assert isinstance(token, str), "Authorization token should be a string."
        assert len(token) > 0, "Authorization token string should not be empty."
        print(f"Received authorization token (first 10 chars): {token[:10]}...")
    except RequestException as e:
        pytest.fail(f"API request failed while fetching authorization token: {e}")
    except ValueError as e:
        pytest.fail(f"Value error (e.g., parsing response) while fetching authorization token: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

# To run this test, ensure WHISK_SESSION_COOKIE is set in your environment.
# Example:
# export WHISK_SESSION_COOKIE="whisk_session=YOUR_COOKIE_HERE"
# And run from the root directory: python -m pytest
#
# Example pytest.ini:
# [pytest]
# markers =
#     api_call: marks tests that make real API calls (and require WHISK_SESSION_COOKIE)
