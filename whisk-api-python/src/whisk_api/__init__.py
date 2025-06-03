# whisk-api-python/src/whisk_api/__init__.py
from .client import WhiskAPI
from .auth import Authenticator # Added Authenticator as it's a core component
from .types import (
    GenerateImageRequest, GenerateImageResponse, ImageModelType, AspectRatioType,
    RefineImageRequest,
    ProjectHistoryItem,
    ImageHistoryItem,
    CreateProjectRequest, CreateProjectResponse, # Added CreateProjectResponse for completeness
    DeleteProjectsRequest, DeleteProjectsResponse,
    RenameProjectRequest, RenameProjectResponse,  # Added RenameProjectResponse for completeness
    AuthorizationTokenResponse # Added for completeness
)
# Import core request function if it's meant to be part of the public API,
# otherwise, it's an internal detail. For now, assume it's internal.
# from .core.request import make_request

__version__ = "0.1.0"

__all__ = [
    "WhiskAPI",
    "Authenticator",
    "GenerateImageRequest",
    "GenerateImageResponse",
    "ImageModelType",
    "AspectRatioType",
    "RefineImageRequest",
    "ProjectHistoryItem",
    "ImageHistoryItem",
    "CreateProjectRequest",
    "CreateProjectResponse",
    "DeleteProjectsRequest",
    "DeleteProjectsResponse",
    "RenameProjectRequest",
    "RenameProjectResponse",
    "AuthorizationTokenResponse",
    "__version__",
]
