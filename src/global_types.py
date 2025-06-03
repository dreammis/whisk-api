from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union, Literal
from enum import Enum

class ImageModel(Enum):
    IMAGEN_2 = "IMAGEN_2"
    IMAGEN_3 = "IMAGEN_3"
    IMAGEN_3_1 = "IMAGEN_3_1"
    IMAGEN_3_5 = "IMAGEN_3_5"
    IMAGEN_3_PORTRAIT = "IMAGEN_3_PORTRAIT"
    IMAGEN_3_LANDSCAPE = "IMAGEN_3_LANDSCAPE"
    IMAGEN_3_PORTRAIT_THREE_FOUR = "IMAGEN_3_PORTRAIT_THREE_FOUR"
    IMAGEN_3_LANDSCAPE_FOUR_THREE = "IMAGEN_3_LANDSCAPE_FOUR_THREE"

class AspectRatio(Enum):
    IMAGE_ASPECT_RATIO_SQUARE = "IMAGE_ASPECT_RATIO_SQUARE"
    IMAGE_ASPECT_RATIO_PORTRAIT = "IMAGE_ASPECT_RATIO_PORTRAIT"
    IMAGE_ASPECT_RATIO_LANDSCAPE = "IMAGE_ASPECT_RATIO_LANDSCAPE"
    IMAGE_ASPECT_RATIO_UNSPECIFIED = "IMAGE_ASPECT_RATIO_UNSPECIFIED"
    IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE = "IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE"
    IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR = "IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR"

@dataclass
class Credentials:
    cookie: str
    authorizationKey: Optional[str] = None

@dataclass
class Result[T]:
    Ok: Optional[T] = None
    Err: Optional[Exception] = None # Changed Error to Exception for Python equivalent

@dataclass
class Request:
    url: str
    headers: Dict[str, str] # Assuming Headers is a dictionary of strings
    method: Literal["GET", "POST", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"]
    body: Optional[str] = None

@dataclass
class Prompt:
    prompt: str
    seed: Optional[int] = None
    projectId: Optional[str] = None
    imageModel: Optional[ImageModel] = None
    aspectRatio: Optional[AspectRatio] = None

@dataclass
class Image:
    seed: int
    prompt: str
    modelNameType: str
    previousMediaGenerationId: str
    workflowId: str
    fingerprintLogRecordId: str

@dataclass
class MediaGenerationId:
    mediaType: str
    workflowId: str
    workflowStepId: str
    mediaKey: str

@dataclass
class Media:
    name: str
    image: Image # Referring to the Image dataclass
    mediaGenerationId: MediaGenerationId

@dataclass
class Projects:
    name: str
    media: Media
    displayName: str
    createTime: str

@dataclass
class Images: # This seems similar to Projects but for images
    name: str
    media: Media
    createTime: str

class MediaVisibility(Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"

@dataclass
class FetchedImageDetails:
    encodedImage: str
    seed: int
    mediaGenerationId: str
    mediaVisibility: MediaVisibility
    prompt: str
    modelNameType: str
    previousMediaGenerationId: str
    workflowId: str
    fingerprintLogRecordId: str

@dataclass
class UserInput:
    userInstructions: str

@dataclass
class MediaInput:
    mediaCategory: Literal["MEDIA_CATEGORY_BOARD"] # Only one value seen

@dataclass
class RecipeInput:
    userInput: UserInput
    mediaInputs: List[MediaInput]

@dataclass
class BackboneMetadata:
    mediaCategory: Literal["MEDIA_CATEGORY_BOARD"]
    recipeInput: RecipeInput

@dataclass
class FetchedImage:
    name: str
    image: FetchedImageDetails
    createTime: str
    backboneMetadata: BackboneMetadata
    mediaGenerationId: MediaGenerationId

@dataclass
class ImageDetails:
    mediaGenerationId: str
    mediaVisibility: MediaVisibility
    prompt: str

@dataclass
class ImageMetadata:
    name: str
    image: ImageDetails # Referring to ImageDetails dataclass
    createTime: str
    backboneMetadata: BackboneMetadata

@dataclass
class GeneratedImage:
    encodedImage: str
    seed: int
    mediaGenerationId: str
    prompt: str
    isMaskEditedImage: Optional[bool] = None
    modelNameType: Optional[str] = None
    workflowId: Optional[str] = None
    fingerprintLogRecordId: Optional[str] = None
    imageModel: Optional[ImageModel] = None

@dataclass
class ImagePanel:
    prompt: str
    generatedImages: List[GeneratedImage]

@dataclass
class GenerationResult:
    imagePanels: List[ImagePanel]
    workflowId: str

@dataclass
class RefinementRequest:
    existingPrompt: str
    newRefinement: str
    base64image: str
    imageId: str # The media key of the image
    seed: Optional[int] = None
    count: Optional[int] = None
    imageModel: Optional[ImageModel] = None
    aspectRatio: Optional[AspectRatio] = None
    projectId: Optional[str] = None
