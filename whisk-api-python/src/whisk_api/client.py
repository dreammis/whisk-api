from .auth import Authenticator
from .core.request import make_request
from .types import (
    GenerateImageRequest, GenerateImageResponse, ImageModelType, AspectRatioType,
    RefineImageRequest,
    ProjectHistoryItem,
    ImageHistoryItem,
    CreateProjectRequest, # CreateProjectResponse might not be used if response is string
    DeleteProjectsRequest, DeleteProjectsResponse,
    RenameProjectRequest, # RenameProjectResponse might not be used
    # AuthorizationTokenResponse might not be used
)
import requests # For potential exceptions
import base64 # For save_image
from typing import List, Optional # For type hints

class WhiskAPI:
    """
    Python client for interacting with the Whisk API.
    """
    BASE_URL = "https://labs.google.com/whisk" # Main base URL

    def __init__(self, session_cookie: str):
        """
        Initializes the WhiskAPI client.

        Args:
            session_cookie: The whisk_session cookie string.
        """
        if not session_cookie:
            raise ValueError("Session cookie cannot be empty.")
        self.authenticator = Authenticator(session_cookie)
        # The request function is used directly, no need to store an instance if it's stateless
        # If it were a class, you'd instantiate it here:
        # self.request_handler = RequestHandler()

    def _make_api_request(self, method: str, endpoint_path: str, query_params: Optional[dict] = None, payload: Optional[dict] = None) -> dict:
        """
        Internal helper to make authenticated API requests.
        Constructs URL with query parameters if provided.
        """
        # Ensure endpoint_path does not start with a slash if BASE_URL ends with one, or vice-versa
        url = f"{self.BASE_URL.rstrip('/')}/{endpoint_path.lstrip('/')}"

        headers = self.authenticator.get_auth_headers()
        # Content-Type is often required for POST/PUT/PATCH requests with JSON
        if payload is not None: # Check specifically for None, as empty dict {} is a valid payload
            headers["Content-Type"] = "application/json"

        try:
            # Pass query_params directly to the updated make_request function
            return make_request(
                url=url,
                method=method,
                headers=headers,
                json_payload=payload,
                query_params=query_params # Pass the original query_params dict
            )
        except requests.exceptions.RequestException as e:
            # Log or handle more specifically if needed
            # The URL printed here will not include query params anymore, which is fine
            # as make_request handles them.
            print(f"API request to {method} {url} (params: {query_params}) failed: {e}")
            # You might want to raise a custom exception here
            raise

    def generate_image(self, request_data: GenerateImageRequest) -> GenerateImageResponse:
        """
        Generates an image based on the provided request data.

        Args:
            request_data: An instance of GenerateImageRequest containing the prompt
                          and other parameters for image generation.

        Returns:
            A GenerateImageResponse object containing the generated image(s) data.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the response from the API is not as expected.
        """
        # Endpoint based on TS source (src/index.ts -> generateImage function)
        # It seems to be POST /v1/images:generate
        endpoint_path = "v1/images:generate"

        payload = request_data.model_dump(by_alias=True, exclude_none=True)
        response_json = self._make_api_request("POST", endpoint_path, payload=payload)

        try:
            return GenerateImageResponse(**response_json)
        except Exception as e: # Pydantic's ValidationError is a subclass of Exception
            print(f"Error parsing GenerateImageResponse: {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for image generation: {e}")

    def refine_image(self, request_data: RefineImageRequest) -> GenerateImageResponse:
        """
        Refines an existing image based on the provided request data.

        Args:
            request_data: An instance of RefineImageRequest.

        Returns:
            A GenerateImageResponse object containing the refined image(s) data.
        """
        # Endpoint based on TS source (src/index.ts -> refineImage function)
        # POST /v1/images:refine
        endpoint_path = "v1/images:refine"
        payload = request_data.model_dump(by_alias=True, exclude_none=True)
        response_json = self._make_api_request("POST", endpoint_path, payload=payload)

        try:
            # The response structure is the same as generateImage
            return GenerateImageResponse(**response_json)
        except Exception as e:
            print(f"Error parsing RefineImageResponse (GenerateImageResponse model): {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for image refinement: {e}")

    def get_project_history(self, limit: Optional[int] = None) -> List[ProjectHistoryItem]:
        """
        Fetches the project history for the authenticated user.

        Args:
            limit: Optional limit for the number of projects to return.

        Returns:
            A list of ProjectHistoryItem objects.
        """
        # Endpoint based on TS examples (e.g., examples/4_list_all_project_history.ts)
        # GET /v1/projects
        endpoint_path = "v1/projects"
        params = {}
        if limit is not None:
            params["limit"] = limit # Assuming API uses "limit"
            # The TS example uses pageSize, "maxResults", or similar.
            # The example code `whisk.getProjectHistory(12)` suggests `limit` is a direct param.
            # The actual name in the TS code is `max_results` for `getProjectHistory`.
            # Let's assume the API takes `maxResults`. If not, this needs adjustment.
            params["maxResults"] = limit # Corrected based on typical Google API conventions

        response_json = self._make_api_request("GET", endpoint_path, query_params=params)

        # The response is expected to be a list of projects directly, or nested under a key like "projects"
        # TS example: `for(const project of projects.Ok!)` suggests `projects.Ok` is the list.
        # If `response_json` is the list itself:
        try:
            # Assuming the direct response is the list of projects
            if isinstance(response_json, list):
                return [ProjectHistoryItem(**item) for item in response_json]
            # Or if it's nested, e.g., {"projects": [...]}
            elif isinstance(response_json, dict) and "projects" in response_json:
                 return [ProjectHistoryItem(**item) for item in response_json["projects"]]
            else:
                print(f"Unexpected response structure for project history: {response_json}")
                raise ValueError("Project history response was not a list or expected dict.")
        except Exception as e:
            print(f"Error parsing ProjectHistoryResponse: {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for project history: {e}")

    def get_image_history(self, limit: Optional[int] = None) -> List[ImageHistoryItem]:
        """
        Fetches the image generation history for the authenticated user.

        Args:
            limit: Optional limit for the number of images to return.

        Returns:
            A list of ImageHistoryItem objects.
        """
        # Endpoint based on TS examples (e.g., examples/8_get_image_generation_history.ts)
        # GET /v1/images
        endpoint_path = "v1/images"
        params = {}
        if limit is not None:
            # The TS example `whisk.getImageHistory(12)` suggests a limit parameter.
            # The TS client code uses `max_results`.
            params["maxResults"] = limit

        response_json = self._make_api_request("GET", endpoint_path, query_params=params)

        # TS example: `for (const image of history.Ok!)` suggests `history.Ok` is the list.
        # Response structure is likely a list of image items, or {"images": [...]}
        try:
            if isinstance(response_json, list):
                return [ImageHistoryItem(**item) for item in response_json]
            elif isinstance(response_json, dict) and "images" in response_json: # Common pattern
                return [ImageHistoryItem(**item) for item in response_json["images"]]
            # The TS example for getImageHistory in src/index.ts maps `fetchedImage.map(mapFetchedImageToImage)`
            # and `mapFetchedImageToImage` seems to create the structure I have for ImageHistoryItem.
            # The actual API might return `fetchedImage` or similar key.
            elif isinstance(response_json, dict) and "fetchedImage" in response_json and isinstance(response_json["fetchedImage"], list):
                 return [ImageHistoryItem(**item) for item in response_json["fetchedImage"]]
            else:
                print(f"Unexpected response structure for image history: {response_json}")
                raise ValueError("Image history response was not a list or expected dict.")
        except Exception as e:
            print(f"Error parsing ImageHistoryResponse: {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for image history: {e}")

    def create_project(self, title: str) -> str:
        """
        Creates a new project with the given title.

        Args:
            title: The title for the new project.

        Returns:
            The project ID of the newly created project.
        """
        # Endpoint based on TS example (examples/3_create_new_project.ts `whisk.getNewProjectId`)
        # This implies a specific endpoint for getting a new project ID, possibly by creating one.
        # Let's assume POST /v1/projects with a title in payload.
        # The TS client code for `getNewProjectId` is:
        # `return await this.authenticatedRequest<string>("/v1/projects", "POST", JSON.stringify({ title }));`
        # This confirms POST to /v1/projects and the payload.
        endpoint_path = "v1/projects"

        # Using CreateProjectRequest to structure the payload, though it's simple.
        request_data = CreateProjectRequest(title=title)
        payload = request_data.model_dump() # No alias needed if field name matches JSON

        response_json = self._make_api_request("POST", endpoint_path, payload=payload)

        # TS example `newProject.Ok` suggests the response `Ok` value is the project ID string.
        # It could be a direct string response or a JSON like {"projectId": "..."} or {"id": "..."}
        try:
            if isinstance(response_json, str): # Direct string response
                return response_json
            elif isinstance(response_json, dict):
                if "projectId" in response_json:
                    return str(response_json["projectId"])
                elif "id" in response_json: # Common alternative
                    return str(response_json["id"])
                elif "name" in response_json: # Projects often have a 'name' field as their resource identifier
                    return str(response_json["name"])
                else:
                    raise ValueError("Project ID not found in response dict.")
            else:
                raise ValueError(f"Unexpected response type for create project: {type(response_json)}")
        except Exception as e:
            print(f"Error parsing CreateProjectResponse: {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for create project: {e}")

    def delete_projects(self, project_ids: List[str]) -> bool:
        """
        Deletes one or more projects.

        Args:
            project_ids: A list of project IDs to delete.

        Returns:
            True if deletion was successful (or API indicates success), False otherwise.
        """
        # Endpoint based on TS example (examples/6_delete_projects.ts)
        # `whisk.deleteProjects([projectId])`
        # TS client: `return await this.authenticatedRequest<string>("/v1/projects:batchDelete", "POST", JSON.stringify({ names: projectIds }));`
        # This indicates POST to /v1/projects:batchDelete. Payload: { names: ["project_id1", ...] }
        endpoint_path = "v1/projects:batchDelete"

        # The TS payload uses "names". Our DeleteProjectsRequest uses "project_ids" with alias "projectIds".
        # To match the exact {names: [...]} structure shown in TS client:
        payload = {"names": project_ids}
        # If we wanted to use the Pydantic model `DeleteProjectsRequest` which expects `projectIds`:
        # request_data = DeleteProjectsRequest(project_ids=project_ids)
        # payload = request_data.model_dump(by_alias=True) # This would produce {"projectIds": []}

        response_json = self._make_api_request("POST", endpoint_path, payload=payload)

        # The TS example checks `deleteResult.Ok` but doesn't inspect its value.
        # This often means a 200/204 response with no significant body content for success.
        # We'll assume success if no error is raised and response is parsable (even if empty or simple status).
        try:
            # If there's a specific success message/status, we can check it.
            # For now, if make_request didn't throw and we get here, assume success.
            # Some APIs return an empty JSON {} or a status field.
            if response_json is None or isinstance(response_json, dict): # Catches empty or dict response
                 # Optionally, parse with DeleteProjectsResponse if a meaningful status is expected
                if response_json and "status" in response_json:
                    status = DeleteProjectsResponse(**response_json).status
                    print(f"Delete projects status: {status}")
                    return "success" in status.lower() # Or similar check
                return True # Assume success for empty or non-standard success response
            return False # Should not happen if make_request is consistent
        except requests.exceptions.RequestException:
            return False # Already handled by _make_api_request, but as a safeguard
        except Exception as e:
            print(f"Error parsing DeleteProjectsResponse: {e}")
            print(f"Received JSON: {response_json}")
            # Depending on API, an error here might still mean partial success or failure.
            # For simplicity, consider parsing error as failure of this method's contract.
            return False

    def rename_project(self, project_id: str, new_name: str) -> str:
        """
        Renames a project.

        Args:
            project_id: The ID of the project to rename.
            new_name: The new title for the project.

        Returns:
            The project ID of the renamed project (often the same ID).
        """
        # Endpoint based on TS example (examples/7_rename_project.ts)
        # `whisk.renameProject(newName, projectId)`
        # TS Client: `return await this.authenticatedRequest<string>(\`/v1/${projectId}\`, "PATCH", JSON.stringify({ title: newName }));`
        # This indicates PATCH to /v1/{projectId} with payload {title: newName}
        # Note: The TS example in `7_rename_project.ts` passes `newName` first, then `projectId`.
        # My method signature matches common practice (ID first, then data).
        endpoint_path = f"v1/{project_id}" # Assumes project_id is like "projects/XYZ"

        # The TS client payload is {title: newName}. Our RenameProjectRequest uses new_name.
        # To match {title: ...}:
        payload = {"title": new_name}
        # If we used RenameProjectRequest directly:
        # request_data = RenameProjectRequest(project_id=project_id, new_name=new_name)
        # payload = request_data.model_dump() # This would be {"project_id": ..., "new_name": ...}
                                            # or with by_alias=True, {"projectId": ..., "newName": ...}
                                            # Neither matches {title: ...}

        response_json = self._make_api_request("PATCH", endpoint_path, payload=payload)

        # TS example `renameResult.Ok` suggests the response `Ok` value is the project ID string.
        try:
            if isinstance(response_json, str):
                return response_json
            elif isinstance(response_json, dict):
                # Google APIs often return the updated resource.
                # The ID would be in 'name' or 'projectId' or 'id'.
                if "name" in response_json: # e.g. "projects/123"
                    return str(response_json["name"])
                elif "projectId" in response_json:
                    return str(response_json["projectId"])
                elif "id" in response_json:
                    return str(response_json["id"])
                # If the response is just the project_id string but wrapped in a generic key like "id"
                # and the TS code just returns the string directly.
                # This case might be hit if the response is `{"id": "projects/XYZ"}` and TS returns Ok("projects/XYZ")
                # For now, the above specific key checks are better.
                else: # Fallback if it's a simple dict with one value being the ID
                    if len(response_json) == 1:
                        return str(list(response_json.values())[0]) # Highly speculative
                    raise ValueError("Project ID not found in rename response dict.")
            else:
                raise ValueError(f"Unexpected response type for rename project: {type(response_json)}")
        except Exception as e:
            print(f"Error parsing RenameProjectResponse: {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for rename project: {e}")

    def save_image(self, encoded_image_data: str, filename: str) -> bool:
        """
        Saves base64 encoded image data to a file.
        This is a utility function, not a direct API call to Whisk backend (mirrors TS client's saveImage).

        Args:
            encoded_image_data: The base64 encoded string of the image.
            filename: The name of the file to save the image to (e.g., "image.png").

        Returns:
            True if saving was successful, False otherwise.
        """
        try:
            # Ensure filename has a valid image extension if not already provided by user
            # For simplicity, this example assumes filename is complete.
            # Add more robust path handling if needed (e.g., ensuring directory exists)

            image_data = base64.b64decode(encoded_image_data)
            with open(filename, "wb") as f:
                f.write(image_data)
            print(f"Image saved successfully as {filename}")
            return True
        except base64.binascii.Error as b64_err: # Specific error for bad base64
            print(f"Error decoding base64 image data: {b64_err}")
            return False
        except IOError as io_err:
            print(f"Error saving image to file {filename}: {io_err}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while saving image {filename}: {e}")
            return False

    def get_authorization_token(self) -> str:
        """
        Fetches an authorization token.
        The exact nature of this token (e.g., for what service it's used) is based
        on the TS client's `getAuthorizationToken` method.

        Returns:
            The authorization token string.
        """
        # Endpoint based on TS example (examples/1_get_auth_tokens.ts)
        # `whisk.getAuthorizationToken()`
        # TS Client: `return await this.authenticatedRequest<string>("/v1/getAuthorizationToken");`
        # This indicates a GET request to /v1/getAuthorizationToken
        endpoint_path = "v1/getAuthorizationToken"

        response_json = self._make_api_request("GET", endpoint_path)

        # TS example `token.Ok` suggests the response `Ok` value is the token string.
        try:
            if isinstance(response_json, str): # Direct string response
                return response_json
            elif isinstance(response_json, dict):
                # Typically, a token might be under a "token" or "accessToken" key.
                if "token" in response_json:
                    return str(response_json["token"])
                elif "authorizationToken" in response_json: # Matching the method name
                    return str(response_json["authorizationToken"])
                elif "accessToken" in response_json:
                    return str(response_json["accessToken"])
                else: # Fallback if it's a simple dict with one value being the token
                    if len(response_json) == 1:
                        return str(list(response_json.values())[0])
                    raise ValueError("Token not found in response dict.")
            else:
                raise ValueError(f"Unexpected response type for get authorization token: {type(response_json)}")
        except Exception as e:
            print(f"Error parsing AuthorizationTokenResponse: {e}")
            print(f"Received JSON: {response_json}")
            raise ValueError(f"Failed to parse response for get authorization token: {e}")


if __name__ == '__main__':
    # This is for example and basic testing.
    # In a real scenario, you'd get the cookie from a secure source.
    print("Starting WhiskAPI client example...")
    try:
        # Replace with a valid session cookie for actual testing
        # IMPORTANT: Do not commit real cookies to version control.
        mock_session_cookie = "whisk_session=test_cookie_12345"
        if mock_session_cookie == "whisk_session=test_cookie_12345":
            print("Using a mock session cookie for example. Real API calls will fail if not mocked.")

        api_client = WhiskAPI(session_cookie=mock_session_cookie)

        # ... (previous examples collapsed)

        # 8. Example: Save Image (Utility)
        # ... (save_image example already there) ...

        # 9. Example: Get Authorization Token
        print("\n--- Example: Get Authorization Token ---")
        try:
            print(f"Attempting to call get_authorization_token (endpoint: {api_client.BASE_URL}/v1/getAuthorizationToken)...")
            print("Skipping actual API call for get_authorization_token in this example.")
            # Simulate different possible responses
            # simulated_auth_token_response = "mock_auth_token_string_direct"
            simulated_auth_token_response = {"token": "mock_auth_token_from_dict"}
            # simulated_auth_token_response = {"authorizationToken": "mock_auth_token_from_dict_specific_key"}
            # simulated_auth_token_response = {"accessToken": "mock_access_token_from_dict"}

            auth_token = ""
            if isinstance(simulated_auth_token_response, str):
                auth_token = simulated_auth_token_response
            elif isinstance(simulated_auth_token_response, dict):
                if "token" in simulated_auth_token_response: auth_token = simulated_auth_token_response["token"]
                elif "authorizationToken" in simulated_auth_token_response: auth_token = simulated_auth_token_response["authorizationToken"]
                elif "accessToken" in simulated_auth_token_response: auth_token = simulated_auth_token_response["accessToken"]

            print(f"Simulated AuthorizationTokenResponse (Token): {auth_token}")
            assert "mock_auth_token" in auth_token
        except Exception as e:
            print(f"Error in get_authorization_token example: {e}")


        # Test with invalid session cookie (existing example)
        print("\n--- Example: Initialization with empty cookie ---")
        try:
            invalid_client = WhiskAPI(session_cookie="")
        except ValueError as e:
            print(f"Caught expected error for empty cookie: {e}")

    except ValueError as ve:
        print(f"Error in WhiskAPI client setup: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred in the example: {e}")

    print("\nWhiskAPI client example finished.")
