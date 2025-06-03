import asyncio
import os
from src.index import Whisk, WhiskApiException
from src.global_types import Credentials

async def main():
    """
    Example script to get the user's credit status using the Whisk client.
    """
    cookie = os.environ.get("COOKIE")
    if not cookie:
        print("Warning: COOKIE environment variable not set. Using placeholder.")
        print("Please set the COOKIE environment variable with your actual cookie value.")
        cookie = "INVALID_COOKIE"  # Placeholder

    # The authorizationKey can be omitted if the cookie is valid
    # as Whisk._check_credentials() will attempt to fetch it.
    # For this example, we rely on that internal mechanism.
    # If you have the token, you could pass it:
    # auth_token = os.environ.get("AUTHORIZATION_KEY")
    # credentials = Credentials(cookie=cookie, authorizationKey=auth_token)
    credentials = Credentials(cookie=cookie)

    try:
        whisk_client = Whisk(credentials=credentials)

        print("Attempting to get credit status...")
        # The get_credit_status method will internally call _check_credentials
        # which fetches the auth token if not already present.
        credit_status = await whisk_client.get_credit_status()

        print("Successfully retrieved credit status.")
        print(f"Credits remaining: {credit_status}")

    except WhiskApiException as e:
        print(f"Error getting credit status: {e}")
        if e.underlying_error:
            print(f"Underlying error: {e.underlying_error}")
    except ValueError as e: # Catch potential ValueError from Whisk constructor
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
