import json
import base64
import copy
import httpx # For type hints if needed, request_async handles actual client
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, cast

from src.global_types import (
    Credentials, FetchedImage, GenerationResult, ImageMetadata, Images, Projects, Prompt,
    RefinementRequest, Result, Request as APIRequest, AspectRatio, ImageModel, Media
)
from src.utils.request_async import request_async

# Custom Exception
class WhiskApiException(Exception):
    def __init__(self, message: str, underlying_error: Optional[Exception] = None):
        super().__init__(message)
        self.underlying_error = underlying_error

class Whisk:
    credentials: Credentials
    _api_key: str = "AIzaSyBtrm0o5ab1c-Ec8ZuLcGt3oJAA5VWt3pY" # Class variable for API key

    def __init__(self, credentials: Credentials):
        if not credentials.cookie or credentials.cookie == "INVALID_COOKIE":
            raise ValueError("Cookie is missing or invalid.")
        self.credentials = copy.deepcopy(credentials)

    async def _handle_api_response(self, response_result: Result[str]) -> Any:
        """
        Helper to handle the Result object from request_async.
        Raises WhiskApiException on Err, otherwise returns parsed JSON or raw text.
        """
        if response_result.Err:
            raise WhiskApiException(f"API request failed: {response_result.Err}", response_result.Err)
        if response_result.Ok is None: # Should not happen if Err is None
             raise WhiskApiException("API request returned empty successful response.")

        try:
            # Handle cases where response might not be JSON
            # For example, if a server error returns HTML or plain text
            if response_result.Ok.strip().startswith("{") or response_result.Ok.strip().startswith("["):
                return json.loads(response_result.Ok)
            return response_result.Ok # Return as text if not clearly JSON
        except json.JSONDecodeError as e:
            raise WhiskApiException(f"Failed to parse JSON response: {response_result.Ok}", e)

    async def _check_credentials(self):
        if not self.credentials.cookie:
            raise WhiskApiException("Credentials are not set. Please provide a valid cookie.")

        if not self.credentials.authorizationKey:
            try:
                token = await self.get_authorization_token()
                self.credentials.authorizationKey = token
            except WhiskApiException as e:
                raise WhiskApiException(f"Failed to get authorization token: {e}", e)


    async def is_available(self) -> bool:
        req = APIRequest(
            body="{}",
            method="POST",
            url="https://aisandbox-pa.googleapis.com/v1:checkAppAvailability",
            headers={
                "Content-Type": "text/plain;charset=UTF-8",
                "X-Goog-Api-Key": self._api_key,
            },
        )
        response_result = await request_async(req)
        response_body = await self._handle_api_response(response_result)

        if not isinstance(response_body, dict):
            raise WhiskApiException(f"Unexpected response structure for is_available: {response_body}")

        return response_body.get("availabilityState") == "AVAILABLE"

    async def get_authorization_token(self) -> str:
        if not self.credentials.cookie:
            raise WhiskApiException("Empty or invalid cookies.")

        req = APIRequest(
            method="GET",
            url="https://labs.google/fx/api/auth/session",
            headers={"Cookie": str(self.credentials.cookie)},
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for get_authorization_token: {parsed_resp}")

        token = parsed_resp.get("access_token")
        if not token:
            raise WhiskApiException(f"Failed to get session token from response: {parsed_resp}")
        return str(token)

    async def get_credit_status(self) -> int:
        await self._check_credentials()
        req_body = {"tool": "BACKBONE", "videoModel": "VEO_2_1_I2V"}
        req = APIRequest(
            method="POST",
            body=json.dumps(req_body),
            url="https://aisandbox-pa.googleapis.com/v1:GetUserVideoCreditStatusAction",
            headers={"Authorization": str(self.credentials.authorizationKey)}, # Assuming bearer not needed here based on TS
        )
        response_result = await request_async(req)
        response_body = await self._handle_api_response(response_result)

        if not isinstance(response_body, dict):
            raise WhiskApiException(f"Unexpected response structure for get_credit_status: {response_body}")

        credits = response_body.get("credits")
        if credits is None:
             raise WhiskApiException(f"Could not find 'credits' in response: {response_body}")
        return int(credits)

    async def get_new_project_id(self, project_title: str) -> str:
        await self._check_credentials()
        req_body = {
            "json": {
                "clientContext": {"tool": "BACKBONE", "sessionId": ";1748266079775"},
                "workflowMetadata": {"workflowName": project_title}
            }
        }
        req = APIRequest(
            method="POST",
            body=json.dumps(req_body),
            url="https://labs.google/fx/api/trpc/media.createOrUpdateWorkflow",
            headers={"Cookie": str(self.credentials.cookie), "Content-Type": "application/json"},
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for get_new_project_id: {parsed_resp}")

        workflow_id = parsed_resp.get("result", {}).get("data", {}).get("json", {}).get("result", {}).get("workflowId")
        if not workflow_id:
            raise WhiskApiException(f"Failed to create new library or parse workflowId: {parsed_resp}")
        return str(workflow_id)

    async def get_project_history(self, limit_count: int) -> List[Projects]:
        await self._check_credentials()
        req_json_payload = {
            "json": {"rawQuery": "", "type": "BACKBONE", "subtype": "PROJECT", "limit": limit_count, "cursor": None},
            "meta": {"values": {"cursor": ["undefined"]}}
        }
        req = APIRequest(
            method="GET",
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
            url=f"https://labs.google/fx/api/trpc/media.fetchUserHistory?input={json.dumps(req_json_payload)}",
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for get_project_history: {parsed_resp}")

        workflow_list = parsed_resp.get("result", {}).get("data", {}).get("json", {}).get("result", {}).get("userWorkflows")
        if not isinstance(workflow_list, list):
            raise WhiskApiException(f"Failed to get project history or parse workflow list: {parsed_resp}")

        # Assuming the structure matches Projects dataclass, direct casting or validation needed here
        # For now, we'll cast, but Pydantic or manual validation would be safer
        return cast(List[Projects], workflow_list)


    async def get_image_history(self, limit_count: int) -> List[Images]:
        await self._check_credentials()
        if limit_count <= 0:
            raise ValueError("Limit count must be greater than 0.")

        req_json_payload = {
            "json": {"rawQuery": "", "type": "BACKBONE", "subtype": "IMAGE", "limit": limit_count, "cursor": None},
            "meta": {"values": {"cursor": ["undefined"]}}
        }
        req = APIRequest(
            method="GET",
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
            url=f"https://labs.google/fx/api/trpc/media.fetchUserHistory?input={json.dumps(req_json_payload)}",
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for get_image_history: {parsed_resp}")

        media_list = parsed_resp.get("result", {}).get("data", {}).get("json", {}).get("result", {}).get("userWorkflows") # userWorkflows seems to be used for images too
        if not isinstance(media_list, list):
            raise WhiskApiException(f"Failed to get image history or parse media list: {parsed_resp}")
        return cast(List[Images], media_list)


    async def get_project_content(self, project_id: str) -> List[ImageMetadata]:
        await self._check_credentials()
        if not project_id:
            raise ValueError("Project ID is required.")

        req_json_payload = {"json": {"workflowId": project_id}}
        req = APIRequest(
            method="GET",
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
            url=f"https://labs.google/fx/api/trpc/media.getProjectWorkflow?input={json.dumps(req_json_payload)}",
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for get_project_content: {parsed_resp}")

        media_list = parsed_resp.get("result", {}).get("data", {}).get("json", {}).get("result", {}).get("media")
        if not isinstance(media_list, list):
            raise WhiskApiException(f"Failed to get project content or parse media list: {parsed_resp}")
        return cast(List[ImageMetadata], media_list)

    async def rename_project(self, new_name: str, project_id: str) -> str:
        # Cookie check is implicitly handled by _check_credentials, but the original had a direct check.
        # We rely on _check_credentials to run first if auth token is needed, or direct cookie use.
        if not self.credentials.cookie:
             raise WhiskApiException("Cookie field is empty")

        req_json_payload = {
            "json": {
                "workflowId": project_id,
                "clientContext": {"sessionId": ";1748333296243", "tool": "BACKBONE", "workflowId": project_id},
                "workflowMetadata": {"workflowName": new_name}
            }
        }
        req = APIRequest(
            method="POST",
            body=json.dumps(req_json_payload),
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
            url="https://labs.google/fx/api/trpc/media.createOrUpdateWorkflow",
        )
        response_result = await request_async(req)
        parsed_body = await self._handle_api_response(response_result)

        if not isinstance(parsed_body, dict):
            raise WhiskApiException(f"Unexpected response structure for rename_project: {parsed_body}")

        if parsed_body.get("error"):
            raise WhiskApiException(f"Failed to rename project: {parsed_body.get('error')}")

        workflow_id = parsed_body.get("result", {}).get("data", {}).get("json", {}).get("result", {}).get("workflowId")
        if not workflow_id:
            raise WhiskApiException(f"Failed to get workflowId from rename response: {parsed_body}")
        return str(workflow_id)

    async def delete_projects(self, project_ids: List[str]) -> bool:
        if not self.credentials.cookie:
             raise WhiskApiException("Cookie field is empty")

        req_json_payload = {"json": {"parent": "userProject/", "names": project_ids}}
        req = APIRequest(
            method="POST",
            body=json.dumps(req_json_payload),
            url="https://labs.google/fx/api/trpc/media.deleteMedia",
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for delete_projects: {parsed_resp}")

        if parsed_resp.get("error"):
            raise WhiskApiException(f"Failed to delete media: {parsed_resp.get('error')}")
        return True


    async def get_media(self, media_key: str) -> FetchedImage:
        await self._check_credentials()
        if not media_key:
            raise ValueError("Media key is required.")

        req_json_payload = {"json": {"mediaKey": media_key}}
        req = APIRequest(
            method="GET",
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
            url=f"https://labs.google/fx/api/trpc/media.fetchMedia?input={json.dumps(req_json_payload)}",
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for get_media: {parsed_resp}")

        image_data = parsed_resp.get("result", {}).get("data", {}).get("json", {}).get("result")
        if not image_data or not isinstance(image_data, dict): # Check if image_data is a dictionary
            raise WhiskApiException(f"Failed to get media or parse image data: {parsed_resp}")

        # Manual dict to FetchedImage conversion or use a library like Pydantic
        # For now, trusting the structure and casting
        return cast(FetchedImage, image_data)

    async def generate_image(self, prompt_details: Prompt) -> GenerationResult:
        await self._check_credentials()

        if not prompt_details or not prompt_details.prompt:
            raise ValueError("Invalid prompt. Please provide a valid prompt.")

        if not prompt_details.projectId:
            try:
                project_id = await self.get_new_project_id("New Project by WhiskClient")
                prompt_details.projectId = project_id
            except WhiskApiException as e:
                 raise WhiskApiException("Failed to auto-create project ID for generate_image", e)


        req_json_payload = {
            "clientContext": {
                "workflowId": prompt_details.projectId,
                "tool": "BACKBONE",
                "sessionId": ";1748281496093" # Static or dynamic?
            },
            "imageModelSettings": {
                "imageModel": prompt_details.imageModel.value if prompt_details.imageModel else ImageModel.IMAGEN_3_5.value,
                "aspectRatio": prompt_details.aspectRatio.value if prompt_details.aspectRatio else AspectRatio.IMAGE_ASPECT_RATIO_LANDSCAPE.value,
            },
            "seed": prompt_details.seed if prompt_details.seed is not None else 0,
            "prompt": prompt_details.prompt,
            "mediaCategory": "MEDIA_CATEGORY_BOARD"
        }

        auth_key = self.credentials.authorizationKey
        if not auth_key: # Should be caught by _check_credentials, but as a safeguard
            raise WhiskApiException("Authorization key not available for generate_image.")

        req = APIRequest(
            method="POST",
            body=json.dumps(req_json_payload),
            url="https://aisandbox-pa.googleapis.com/v1/whisk:generateImage",
            headers={
                "Content-Type": "application/json", # Original was text/plain but this seems more appropriate for JSON body
                "Authorization": f"Bearer {auth_key}",
            },
        )
        response_result = await request_async(req)
        parsed_resp = await self._handle_api_response(response_result)

        if not isinstance(parsed_resp, dict):
            raise WhiskApiException(f"Unexpected response structure for generate_image: {parsed_resp}")

        if parsed_resp.get("error"):
            raise WhiskApiException(f"Failed to generate image: {parsed_resp.get('error')}")
        return cast(GenerationResult, parsed_resp)


    async def refine_image(self, refinement_req: RefinementRequest) -> GenerationResult:
        await self._check_credentials()

        # Defaults
        seed = refinement_req.seed if refinement_req.seed is not None else 0
        aspect_ratio = refinement_req.aspectRatio if refinement_req.aspectRatio else AspectRatio.IMAGE_ASPECT_RATIO_LANDSCAPE
        image_model = refinement_req.imageModel if refinement_req.imageModel else ImageModel.IMAGEN_3_5
        count = refinement_req.count if refinement_req.count is not None else 1

        # Step 1: Generate Rewritten Prompt
        req_json_step1 = {
            "json": {
                "existingPrompt": refinement_req.existingPrompt,
                "textInput": refinement_req.newRefinement,
                "editingImage": {
                    "imageId": refinement_req.imageId,
                    "base64Image": refinement_req.base64image,
                    "category": "STORYBOARD", # Static as per TS
                    "prompt": refinement_req.existingPrompt,
                    "mediaKey": refinement_req.imageId, # Same as imageId
                    "isLoading": False, "isFavorite": None, "isActive": True, "isPreset": False,
                    "isSelected": False, "index": 0,
                    "imageObjectUrl": "blob:https://labs.google/1c612ac4-ecdf-4f77-9898-82ac488ad77f", # Static
                    "recipeInput": {"mediaInputs": [], "userInput": {"userInstructions": refinement_req.existingPrompt}},
                    "currentImageAction": "REFINING", # Static
                    "seed": seed
                },
                "sessionId": ";1748338835952" # Static
            },
            "meta": {"values": {"editingImage.isFavorite": ["undefined"]}}
        }

        req_step1 = APIRequest(
            method="POST",
            body=json.dumps(req_json_step1),
            url="https://labs.google/fx/api/trpc/backbone.generateRewrittenPrompt",
            headers={"Content-Type": "application/json", "Cookie": str(self.credentials.cookie)},
        )
        response_result_step1 = await request_async(req_step1)
        parsed_resp_step1 = await self._handle_api_response(response_result_step1)

        if not isinstance(parsed_resp_step1, dict) or parsed_resp_step1.get("error"):
            raise WhiskApiException(f"Failed to get rewritten prompt: {parsed_resp_step1.get('error') or parsed_resp_step1}")

        new_prompt = parsed_resp_step1.get("result", {}).get("data", {}).get("json")
        if not new_prompt:
            raise WhiskApiException(f"Failed to extract new prompt from response: {parsed_resp_step1}")

        # Step 2: Generate Image with New Prompt
        req_json_step2 = {
            "userInput": {
                "candidatesCount": count, "seed": seed, "prompts": [new_prompt],
                "mediaCategory": "MEDIA_CATEGORY_BOARD",
                "recipeInput": {"userInput": {"userInstructions": new_prompt}, "mediaInputs": []}
            },
            "clientContext": {
                "sessionId": ";1748338835952", "tool": "BACKBONE",
                "workflowId": refinement_req.projectId,
            },
            "modelInput": {"modelNameType": image_model.value},
            "aspectRatio": aspect_ratio.value
        }

        auth_key = self.credentials.authorizationKey
        if not auth_key:
             raise WhiskApiException("Authorization key not available for refine_image step 2.")


        req_step2 = APIRequest(
            method="POST",
            body=json.dumps(req_json_step2),
            url="https://aisandbox-pa.googleapis.com/v1:runBackboneImageGeneration",
            headers={"Content-Type": "text/plain;charset=UTF-8", "Authorization": f"Bearer {auth_key}"},
        )
        response_result_step2 = await request_async(req_step2)
        parsed_resp_step2 = await self._handle_api_response(response_result_step2)

        if not isinstance(parsed_resp_step2, dict) or parsed_resp_step2.get("error"):
            raise WhiskApiException(f"Failed to generate refined image: {parsed_resp_step2.get('error') or parsed_resp_step2}")

        return cast(GenerationResult, parsed_resp_step2)

    def save_image(self, image_base64: str, file_name: str) -> None:
        """Saves a base64 encoded image string to a file."""
        try:
            image_bytes = base64.b64decode(image_base64)
            file_path = Path(file_name)
            file_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
            with open(file_path, "wb") as f:
                f.write(image_bytes)
        except (base64.binascii.Error, IOError) as e: # Catch decoding and I/O errors
            raise WhiskApiException(f"Failed to save image to {file_name}: {e}", e)


    async def save_image_direct(self, image_id: str, file_name: str) -> None:
        """Fetches an image by its ID and saves it to a file."""
        try:
            media_data = await self.get_media(image_id)
            # The FetchedImage structure needs to be accurately mapped here
            # Assuming media_data is a dict-like structure from JSON:
            # FetchedImage -> image: FetchedImageDetails -> encodedImage: str

            # Check if media_data is a dict and has the expected nested structure
            if not isinstance(media_data, dict) or \
               'image' not in media_data or \
               not isinstance(media_data['image'], dict) or \
               'encodedImage' not in media_data['image']:
                raise WhiskApiException(f"Unexpected structure for media data: {media_data}")

            encoded_image_str = media_data['image']['encodedImage']
            if not isinstance(encoded_image_str, str):
                raise WhiskApiException(f"Encoded image is not a string: {encoded_image_str}")

            self.save_image(encoded_image_str, file_name)
        except WhiskApiException as e:
            # Re-raise if it's already our custom type, or wrap if it's a general one from get_media
            raise WhiskApiException(f"Failed to save image directly for ID {image_id} to {file_name}: {e}", e)
        except Exception as e: # Catch any other unexpected errors
            raise WhiskApiException(f"An unexpected error occurred in save_image_direct: {e}", e)

# Example usage (optional, for testing)
# async def main():
#     # Requires valid credentials
#     # creds = Credentials(cookie="YOUR_COOKIE_HERE")
#     # whisk_client = Whisk(creds)
#     # try:
#     #     # print(await whisk_client.is_available())
#     #     # token = await whisk_client.get_authorization_token()
#     #     # print(f"Token: {token}")
#     #     # whisk_client.credentials.authorizationKey = token # Set token for further calls
#     #     # projects = await whisk_client.get_project_history(5)
#     #     # print(projects)
#     # except WhiskApiException as e:
#     #     print(f"Error: {e}")

# if __name__ == "__main__":
#     import asyncio
#     # asyncio.run(main())
pass
