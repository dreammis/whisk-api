import asyncio
import os
from src.index import Whisk, WhiskApiException
from src.global_types import Credentials

async def main():
    """
    Example script to create a new project and get its ID using the Whisk client.
    """
    cookie = os.environ.get("COOKIE")
    if not cookie:
        print("Warning: COOKIE environment variable not set. Using placeholder.")
        print("Please set the COOKIE environment variable with your actual cookie value.")
        cookie = "INVALID_COOKIE"  # Placeholder

    # Initialize credentials (auth token will be handled internally by Whisk if needed)
    credentials = Credentials(cookie=cookie)

    project_title = "My Python Project" # Example project title

    try:
        whisk_client = Whisk(credentials=credentials)

        print(f"Attempting to create a new project titled: '{project_title}'...")
        # Call the get_new_project_id method
        project_id = await whisk_client.get_new_project_id(project_title)

        print("Successfully created new project.")
        print(f"New project ID: {project_id}")

    except WhiskApiException as e:
        print(f"Error creating new project: {e}")
        if e.underlying_error:
            print(f"Underlying error: {e.underlying_error}")
    except ValueError as e: # Catch potential ValueError from Whisk constructor
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
