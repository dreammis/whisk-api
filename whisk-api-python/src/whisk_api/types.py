from typing import List, Optional, Literal
from pydantic import BaseModel, Field

ImageModelType = Literal[
    "IMAGEN_2",
    "IMAGEN_3",
    "IMAGEN_3_1",
    "IMAGEN_3_5",
    "IMAGEN_3_PORTRAIT",
    "IMAGEN_3_LANDSCAPE",
    "IMAGEN_3_PORTRAIT_THREE_FOUR",
    "IMAGEN_3_LANDSCAPE_FOUR_THREE",
]

AspectRatioType = Literal[
    "IMAGE_ASPECT_RATIO_SQUARE",
    "IMAGE_ASPECT_RATIO_PORTRAIT",
    "IMAGE_ASPECT_RATIO_LANDSCAPE",
    "IMAGE_ASPECT_RATIO_UNSPECIFIED",
    "IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE",
    "IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR",
]

class GenerateImageRequest(BaseModel):
    """
    Request model for generating an image.
    Based on the Prompt interface in global.types.ts
    """
    prompt: str
    seed: Optional[int] = None
    project_id: Optional[str] = Field(None, alias="projectId")
    image_model: Optional[ImageModelType] = Field(None, alias="imageModel")
    aspect_ratio: Optional[AspectRatioType] = Field(None, alias="aspectRatio")

class GeneratedImage(BaseModel):
    """
    Represents a single generated image with its details.
    """
    encoded_image: str = Field(..., alias="encodedImage")
    seed: int
    media_generation_id: str = Field(..., alias="mediaGenerationId")
    prompt: str
    image_model: Optional[ImageModelType] = Field(None, alias="imageModel") # Present in TS GeneratedImage
    # Optional fields from TS GeneratedImage that might be useful
    is_mask_edited_image: Optional[bool] = Field(None, alias="isMaskEditedImage")
    model_name_type: Optional[str] = Field(None, alias="modelNameType")
    workflow_id: Optional[str] = Field(None, alias="workflowId")
    fingerprint_log_record_id: Optional[str] = Field(None, alias="fingerprintLogRecordId")


class ImagePanel(BaseModel):
    """
    Contains a prompt and the list of images generated for that prompt.
    """
    prompt: str
    generated_images: List[GeneratedImage] = Field(..., alias="generatedImages")

class GenerateImageResponse(BaseModel):
    """
    Response model for the image generation endpoint.
    Based on the GenerationResult interface in global.types.ts
    """
    image_panels: List[ImagePanel] = Field(..., alias="imagePanels")
    workflow_id: str = Field(..., alias="workflowId")

if __name__ == '__main__':
    # Example Usage for GenerateImageRequest
    request_data = {
        "prompt": "A beautiful sunset over the mountains",
        "seed": 12345,
        "imageModel": "IMAGEN_3",
        "aspectRatio": "IMAGE_ASPECT_RATIO_LANDSCAPE"
    }
    try:
        generate_request = GenerateImageRequest(**request_data)
        print("GenerateImageRequest (from dict):")
        print(generate_request.model_dump_json(indent=2, by_alias=True))

        generate_request_direct = GenerateImageRequest(
            prompt="A serene lake at dawn",
            projectId="my-project-123"
        )
        print("\nGenerateImageRequest (direct instantiation):")
        print(generate_request_direct.model_dump_json(indent=2, by_alias=True))

    except Exception as e:
        print(f"Error creating GenerateImageRequest: {e}")

    # Example Usage for GenerateImageResponse
    response_data = {
        "imagePanels": [
            {
                "prompt": "A beautiful sunset over the mountains",
                "generatedImages": [
                    {
                        "encodedImage": "base64encodedstring...",
                        "seed": 12345,
                        "mediaGenerationId": "media-gen-id-1",
                        "prompt": "A beautiful sunset over the mountains",
                        "imageModel": "IMAGEN_3"
                    },
                    {
                        "encodedImage": "base64encodedstring2...",
                        "seed": 67890,
                        "mediaGenerationId": "media-gen-id-2",
                        "prompt": "A beautiful sunset over the mountains, variation"
                    }
                ]
            }
        ],
        "workflowId": "workflow-abc-123"
    }
    try:
        generate_response = GenerateImageResponse(**response_data)
        print("\nGenerateImageResponse (from dict):")
        print(generate_response.model_dump_json(indent=2, by_alias=True))

        # Accessing data
        if generate_response.image_panels and generate_response.image_panels[0].generated_images:
            print(f"\nFirst image's encoded data: {generate_response.image_panels[0].generated_images[0].encoded_image}")

    except Exception as e:
        print(f"Error creating GenerateImageResponse: {e}")


class RefineImageRequest(BaseModel):
    """
    Request model for refining an image.
    Based on the RefinementRequest interface in global.types.ts
    """
    existing_prompt: str = Field(..., alias="existingPrompt")
    new_refinement: str = Field(..., alias="newRefinement")
    base64_image: str = Field(..., alias="base64image")
    image_id: str = Field(..., alias="imageId") #  The media key of the image to refine
    seed: Optional[int] = None
    count: Optional[int] = None # Number of images to generate?
    image_model: Optional[ImageModelType] = Field(None, alias="imageModel")
    aspect_ratio: Optional[AspectRatioType] = Field(None, alias="aspectRatio")
    project_id: Optional[str] = Field(None, alias="projectId")


# --- Project History ---
class ProjectHistoryItem(BaseModel):
    """
    Represents a single project in the project history.
    Based on the Projects interface in global.types.ts and example output.
    """
    name: str  # This seems to be the project ID
    display_name: str = Field(..., alias="displayName")
    create_time: str = Field(..., alias="createTime")
    media: Optional[dict] = None # media field is complex, include as dict for now.

# Response is List[ProjectHistoryItem]


# --- Image History ---
class ImageHistoryItemImageDetails(BaseModel):
    """
    Details of the image within media for image history.
    """
    prompt: str
    model_name_type: str = Field(..., alias="modelNameType")
    # seed: Optional[int] = None # Not directly in example's media.image but in FetchedImage
    # media_generation_id: Optional[str] = Field(None, alias="mediaGenerationId") # Also not directly in example

class ImageHistoryItemMedia(BaseModel):
    """
    Media object for image history item.
    """
    image: ImageHistoryItemImageDetails
    # name: Optional[str] = None # Example doesn't show 'name' inside 'media'
    # media_generation_id: Optional[dict] = None # Example doesn't show this nested here

class ImageHistoryItem(BaseModel):
    """
    Represents a single image in the image generation history.
    Based on Images interface and examples/8_get_image_generation_history.ts.
    """
    name: str # This is the image ID (e.g., "users/.../medias/...")
    create_time: str = Field(..., alias="createTime")
    media: ImageHistoryItemMedia

# Response is List[ImageHistoryItem]


import time # Required for default_factory in CreateProjectClientContext

# --- Create Project (TRPC: media.createOrUpdateWorkflow) ---
class CreateProjectClientContext(BaseModel):
    tool: str = "BACKBONE"
    session_id: str = Field(default_factory=lambda: f";{int(time.time() * 1000)}", alias="sessionId")

class CreateProjectWorkflowMetadata(BaseModel):
    workflow_name: str = Field(..., alias="workflowName") # Python: workflow_name, JSON: workflowName
    class Config:
        populate_by_name = True

class CreateProjectInnerPayload(BaseModel):
    client_context: CreateProjectClientContext = Field(default_factory=CreateProjectClientContext, alias="clientContext")
    workflow_metadata: CreateProjectWorkflowMetadata # Python: workflow_metadata, JSON: workflowMetadata (no alias needed if dict key matches)

    class Config:
        populate_by_name = True # Allow initialization by either field name or alias

class CreateProjectTrpcRequest(BaseModel): # New name for clarity
    json_payload: CreateProjectInnerPayload = Field(..., alias="json")
    class Config:
        populate_by_name = True


# Models for parsing the TRPC response for create_project
class CreateProjectTrpcResponseResultDataResult(BaseModel):
    workflow_id: str = Field(..., alias="workflowId")

class CreateProjectTrpcResponseResultDataJson(BaseModel):
    result: CreateProjectTrpcResponseResultDataResult

class CreateProjectTrpcResponseResultData(BaseModel):
    json_data: CreateProjectTrpcResponseResultDataJson = Field(..., alias="json") # Assuming the 'json' key holds this structure

class CreateProjectTrpcResponseResult(BaseModel):
    data: CreateProjectTrpcResponseResultData

class CreateProjectTrpcResponse(BaseModel):
    result: CreateProjectTrpcResponseResult


# --- Delete Projects (TRPC: media.deleteMedia) ---
class DeleteProjectsInnerPayload(BaseModel):
    parent: str = "userProject/" # Static value
    names: List[str] # List of workflowIds

class DeleteProjectsTrpcRequest(BaseModel):
    json_payload: DeleteProjectsInnerPayload = Field(..., alias="json")
    class Config:
        populate_by_name = True

# No specific response model for delete if just checking for errors,
# but if there's a success structure, it could be added.
# For now, client will check for `error` field in the response dict.
# A generic error response might look like:
class TrpcError(BaseModel):
    code: int
    message: str
    # possibly other fields

class TrpcErrorResponse(BaseModel):
    error: TrpcError


# --- Rename Project ---
# Uses "media.createOrUpdateWorkflow" like create_project.
# TS renameProject payload:
# { "json": { "workflowId": projectId, "clientContext": { "sessionId": ";...", "tool": "BACKBONE", "workflowId": projectId }, "workflowMetadata": { "workflowName": newName } } }

class RenameProjectWorkflowMetadata(BaseModel):
    workflow_name: str = Field(..., alias="workflowName")
    class Config:
        populate_by_name = True

class RenameProjectInnerPayload(BaseModel):
    workflow_id: str = Field(..., alias="workflowId")
    client_context: CreateProjectClientContext = Field(default_factory=CreateProjectClientContext, alias="clientContext")
    workflow_metadata: RenameProjectWorkflowMetadata

    class Config:
        populate_by_name = True

class RenameProjectTrpcRequest(BaseModel): # New name for clarity
    json_payload: RenameProjectInnerPayload = Field(..., alias="json")
    class Config:
        populate_by_name = True

# Rename response is also a workflowId from a similar structure as create.
# We can reuse CreateProjectTrpcResponse or make a specific one if slightly different.
# For now, assume client will parse similarly to create_project.


# --- Project History ---
# ... (rest of the types file from before, unchanged for this diff) ...
class ProjectHistoryItem(BaseModel):
    """
    Represents a single project in the project history.
    Based on the Projects interface in global.types.ts and example output.
    """
    name: str  # This seems to be the project ID
    display_name: str = Field(..., alias="displayName")
    create_time: str = Field(..., alias="createTime")
    media: Optional[dict] = None # media field is complex, include as dict for now.

# Response is List[ProjectHistoryItem]


# --- Image History ---
class ImageHistoryItemImageDetails(BaseModel):
    """
    Details of the image within media for image history.
    """
    prompt: str
    model_name_type: str = Field(..., alias="modelNameType")
    # seed: Optional[int] = None # Not directly in example's media.image but in FetchedImage
    # media_generation_id: Optional[str] = Field(None, alias="mediaGenerationId") # Also not directly in example

class ImageHistoryItemMedia(BaseModel):
    """
    Media object for image history item.
    """
    image: ImageHistoryItemImageDetails
    # name: Optional[str] = None # Example doesn't show 'name' inside 'media'
    # media_generation_id: Optional[dict] = None # Example doesn't show this nested here

class ImageHistoryItem(BaseModel):
    """
    Represents a single image in the image generation history.
    Based on Images interface and examples/8_get_image_generation_history.ts.
    """
    name: str # This is the image ID (e.g., "users/.../medias/...")
    create_time: str = Field(..., alias="createTime")
    media: ImageHistoryItemMedia

# Response is List[ImageHistoryItem]


# --- CreateProjectResponse (Original, potentially unused if client returns str for old endpoint) ---
class CreateProjectResponse(BaseModel):
    project_id: str

# --- DeleteProjectsResponse (Original, potentially unused if client returns bool for old endpoint) ---
class DeleteProjectsResponse(BaseModel):
    status: str

# --- RenameProjectResponse (Original, potentially unused if client returns str for old endpoint) ---
class RenameProjectResponse(BaseModel):
    project_id: str


# --- Get Authorization Token (Auth Session) ---
# Response from https://labs.google/fx/api/auth/session
# is expected to be like {"access_token": "...", ...}
class AuthSessionResponse(BaseModel):
    access_token: str
    # The actual response might contain other fields like 'user_id', 'email', etc.
    # but we only need 'access_token' for the client method's current purpose.
    # Other fields can be added here if they become relevant.

# Old request models that might be deprecated by TRPC changes:
# class CreateProjectRequest(BaseModel): title: str # Replaced by CreateProjectTrpcRequest
# class DeleteProjectsRequest(BaseModel): project_ids: List[str] = Field(..., alias="projectIds") # Replaced by DeleteProjectsTrpcRequest
# class RenameProjectRequest(BaseModel): project_id: str = Field(..., alias="projectId"); new_name: str = Field(..., alias="newName") # Potentially replaced by RenameProjectTrpcRequest
class RenameProjectRequest(BaseModel):
    project_id: str = Field(..., alias="projectId")
    new_name: str = Field(..., alias="newName")

# TS example: renameResult.Ok is the project ID string.
# Similar to CreateProject, if it's just a string, client handles.
# If it's {"projectId": "value"}, this model is suitable.
class RenameProjectResponse(BaseModel):
    project_id: str


# --- Get Authorization Token (Auth Session) ---
# Response from https://labs.google/fx/api/auth/session
# is expected to be like {"access_token": "...", ...}
class AuthSessionResponse(BaseModel):
    access_token: str
    # The actual response might contain other fields like 'user_id', 'email', etc.
    # but we only need 'access_token' for the client method's current purpose.
    # Other fields can be added here if they become relevant.
