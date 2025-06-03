import os
# import sys # No longer needed typically

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from whisk_api import WhiskAPI # Updated import
from requests.exceptions import RequestException

def example_get_credit_status():
    """
    Example related to fetching user status, potentially including credit status.
    Note: The Python client does not have a dedicated `get_credit_status` method.
    This example demonstrates fetching the authorization token, which might be
    related or a prerequisite.
    """
    print("--- Example: Get User/Credit Status (via Auth Token) ---")

    session_cookie = os.environ.get("WHISK_SESSION_COOKIE")
    if not session_cookie:
        print("Error: WHISK_SESSION_COOKIE environment variable not set.")
        return

    try:
        whisk = WhiskAPI(session_cookie=session_cookie)

        print("Attempting to fetch authorization token (as a proxy for user status)...")
        # The TS example for getCreditStatus is very similar to getAuthorizationToken.
        # We'll call get_authorization_token and discuss credit status in comments.
        token_string = whisk.get_authorization_token()

        if token_string:
            print("Successfully fetched authorization token.")
            print(f"Authorization Token: {token_string}")
            print("\nNote on Credit Status:")
            print("The current Python client does not have a specific 'get_credit_status' method.")
            print("Credit status information might be part of a user profile endpoint not yet implemented,")
            print("or implicitly available based on the validity of the authorization token/session.")
            print("Please refer to the Whisk API documentation for details on how to fetch credit status.")
            # If the token response were a JSON object that included credit details, you would parse it here.
            # For example, if token_string was a dict: credit_info = token_string.get("credits")
        else:
            print("Failed to fetch authorization token.")

    except RequestException as e:
        print(f"API Request Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Get User/Credit Status Example Finished ---")

if __name__ == "__main__":
    example_get_credit_status()
