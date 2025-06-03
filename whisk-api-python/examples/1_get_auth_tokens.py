import os
# sys path manipulation no longer needed if package installed or PYTHONPATH set
# import sys

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI # Updated import
from requests.exceptions import RequestException

def example_get_auth_token():
    """
    Example demonstrating how to fetch the authorization token.
    """
    print("--- Example: Get Authorization Token ---")

    # Initialize the WhiskAPI client
    # The session cookie should be set as an environment variable 'WHISK_SESSION_COOKIE'
    # or replaced with a placeholder if you intend to input it manually.
    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        print("Please set it with your whisk_session cookie value.")
        print("Example: export WHISK_SESSION_COOKIE=\"whisk_session=YOUR_ACTUAL_COOKIE_VALUE\"")
        return

    try:
        # Whisk API client initialization
        whisk = WhiskAPI(session_cookie=session_cookie)

        # Fetch the authorization token
        print("Attempting to fetch authorization token...")
        # In the Python client, get_authorization_token() is expected to make the API call
        # and return the token string directly, or raise an exception.
        token_string = whisk.get_authorization_token()

        if token_string:
            print("Successfully fetched authorization token.")
            # The Python client's get_authorization_token method is designed to return the token string directly.
            # If it were to return a model, you'd access token_string.token
            print(f"Authorization Token: {token_string}")
            # Note: The TS example has `token.Ok`, our Python client returns the string directly or raises error.
        else:
            # This case might not be reached if errors cause exceptions.
            print("Failed to fetch authorization token, no token returned.")

    except RequestException as e:
        print(f"API Request Error: Failed to fetch authorization token. {e}")
    except ValueError as e:
        print(f"Value Error: Could not process the response or input. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Get Authorization Token Example Finished ---")

if __name__ == "__main__":
    example_get_auth_token()
