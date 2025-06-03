import asyncio
import os
from src.index import Whisk, WhiskApiException
from src.global_types import Credentials

async def main():
    """
    Example script to get an authorization token using the Whisk client.
    """
    cookie = os.environ.get("COOKIE")
    if not cookie:
        print("Warning: COOKIE environment variable not set. Using placeholder.")
        print("Please set the COOKIE environment variable with your actual cookie value.")
        cookie = "INVALID_COOKIE" # Placeholder

    try:
        # Initialize Whisk with credentials
        credentials = Credentials(cookie=cookie)
        whisk_client = Whisk(credentials=credentials)

        print("Attempting to get authorization token...")
        # Call the get_authorization_token method
        token = await whisk_client.get_authorization_token()

        # If the call succeeds, the token is returned directly
        print("Successfully retrieved authorization token.")
        print("Authorization token:", token)

        # You can now update the client's credentials if you want to use this token for subsequent calls
        # within the same Whisk instance in a more complex script.
        # whisk_client.credentials.authorizationKey = token
        # print("Authorization token set in Whisk client instance.")

    except WhiskApiException as e:
        print(f"Error getting authorization token: {e}")
        if e.underlying_error:
            print(f"Underlying error: {e.underlying_error}")
    except ValueError as e: # Catch potential ValueError from Whisk constructor
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # In Python 3.7+ asyncio.run() is the standard way to run async main functions
    asyncio.run(main())
