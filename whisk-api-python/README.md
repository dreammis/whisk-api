# Whisk API Python

<!-- Python Version Badge -->
[![PyPI version](https://img.shields.io/pypi/v/whisk-api-python.svg?style=flat-square)](https://pypi.org/project/whisk-api-python/) <!-- Placeholder if you publish -->
[![Python Version](https://img.shields.io/pypi/pyversions/whisk-api-python.svg?style=flat-square)](https://pypi.org/project/whisk-api-python/) <!-- Placeholder -->
<!-- Tests Badge - Will need to be updated if CI is set up for Python project -->
<!-- [![Test](https://github.com/your-github-username/whisk-api-python/actions/workflows/test.yaml/badge.svg)](https://github.com/your-github-username/whisk-api-python/actions/workflows/test.yaml) -->
[![License](https://img.shields.io/github/license/rohitaryal/whisk-api.svg)](https://github.com/rohitaryal/whisk-api/blob/main/LICENSE) <!-- Assuming same license -->

An unofficial Python API wrapper for Google Labs' Whisk image generation platform. This project is a Python adaptation of the original TypeScript/JavaScript library [whisk-api by @rohitaryal](https://github.com/rohitaryal/whisk-api).

## Features

- **Image Generation**: Create high-quality images from text prompts.
- **Image Refinement**: Enhance and modify existing generated images.
- **Project Management**: Organize generations into projects with create, list, rename, and delete operations.
- **Media Management**: Access image generation history and save images.
- **Multiple Models**: Support for various Imagen models with different capabilities (as supported by the API).
- **Typed Interface**: Utilizes Pydantic models for request and response objects, providing a degree of type safety and data validation.

## Installation

1.  **From PyPI (once published):**
    ```bash
    pip install whisk-api-python
    ```
    *(Note: This name is a placeholder; actual PyPI name might differ or not be available yet.)*

2.  **From source (local development/direct use):**
    Clone this repository:
    ```bash
    git clone https://github.com/your-github-username/whisk-api-python.git # Or the actual fork/repo URL
    cd whisk-api-python
    ```
    Install the package in editable mode:
    ```bash
    pip install -e .
    ```
    For development, install test dependencies as well:
    ```bash
    pip install -r requirements.txt # Ensure pytest is in requirements.txt
    ```

## Quick Start

```python
import os
from whisk_api import WhiskAPI, GenerateImageRequest
from whisk_api.types import ImageModelType, AspectRatioType # For specific model/aspect ratio literals
from requests.exceptions import RequestException

# Initialize the client with your Google Labs session cookie
# It's recommended to use an environment variable for the cookie
try:
    session_cookie = os.environ["WHISK_SESSION_COOKIE"]
except KeyError:
    print("Error: WHISK_SESSION_COOKIE environment variable not set.")
    print("Please set it: export WHISK_SESSION_COOKIE='whisk_session=YOUR_COOKIE_VALUE'")
    exit(1)

whisk = WhiskAPI(session_cookie=session_cookie)

try:
    # Generate an image
    print("Generating an image...")
    gen_request = GenerateImageRequest(
        prompt="A futuristic cityscape with flying cars, neon lights, cinematic lighting",
        image_model=ImageModelType.IMAGEN_3, # Example: Using Imagen 3
        aspect_ratio=AspectRatioType.IMAGE_ASPECT_RATIO_LANDSCAPE # Example: Landscape
    )

    response = whisk.generate_image(gen_request)

    if response and response.image_panels and response.image_panels[0].generated_images:
        print("Image generated successfully!")
        first_image = response.image_panels[0].generated_images[0]
        print(f"  Media ID: {first_image.media_generation_id}")
        print(f"  Seed: {first_image.seed}")

        # Save the image
        filename = "futuristic_city.png"
        if whisk.save_image(first_image.encoded_image, filename):
            print(f"  Image saved as {filename}")
        else:
            print(f"  Failed to save image as {filename}")
    else:
        print("Image generation failed or no image data in response.")

except RequestException as e:
    print(f"API Request Error: {e}")
except ValueError as e: # Pydantic validation errors or other value errors
    print(f"Data Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Authentication

You'll need to obtain your Google Labs session cookie:

1.  Visit [labs.google.com/fx/tools/whisk](https://labs.google.com/fx/tools/whisk) in your browser.
2.  Open your browser's developer tools (usually by pressing F12).
3.  Navigate to the "Application" (or "Storage" in Firefox) tab.
4.  Under "Cookies", find the cookies for `labs.google.com`.
5.  Copy the **entire value** of the `whisk_session` cookie (it will look something like `whisk_session=ALPHANUMERIC_STRING...`).
6.  Set this value as an environment variable named `WHISK_SESSION_COOKIE`. For example:
    ```bash
    export WHISK_SESSION_COOKIE="whisk_session=YOUR_ACTUAL_COOKIE_VALUE"
    ```
    The Python client expects this environment variable to be set for initializing `WhiskAPI`.

## Supported Models

The underlying Whisk API supports various image generation models. You can specify these in your requests. The available models (as per the original library) include:

| Model Name (in API)             | Python `ImageModelType` Literal        | Description                       |
|---------------------------------|----------------------------------------|-----------------------------------|
| `IMAGEN_2`                      | `"IMAGEN_2"`                           | Second generation model           |
| `IMAGEN_3`                      | `"IMAGEN_3"`                           | Third generation model            |
| `IMAGEN_3_1`                    | `"IMAGEN_3_1"`                         | Enhanced Imagen 3                 |
| `IMAGEN_3_5`                    | `"IMAGEN_3_5"`                         | (Assumed, based on pattern)       |
| `IMAGEN_3_PORTRAIT`             | `"IMAGEN_3_PORTRAIT"`                  | Portrait-optimized                |
| `IMAGEN_3_LANDSCAPE`            | `"IMAGEN_3_LANDSCAPE"`                 | Landscape-optimized               |
| `IMAGEN_3_PORTRAIT_THREE_FOUR`  | `"IMAGEN_3_PORTRAIT_THREE_FOUR"`       | Portrait 3:4 aspect ratio         |
| `IMAGEN_3_LANDSCAPE_FOUR_THREE` | `"IMAGEN_3_LANDSCAPE_FOUR_THREE"`      | Landscape 4:3 aspect ratio        |

*(Note: Model availability is subject to Google's API and may change.)*

## Examples

The library includes usage examples in the [`whisk-api-python/examples/`](./examples/) directory:

- [`1_get_auth_tokens.py`](./examples/1_get_auth_tokens.py): Getting authorization tokens.
- [`2_get_credit_status.py`](./examples/2_get_credit_status.py): Placeholder for credit status (uses auth token).
- [`3_create_new_project.py`](./examples/3_create_new_project.py): Creating projects.
- [`4_list_all_project_history.py`](./examples/4_list_all_project_history.py): Managing project history.
- [`5_get_content_of_projects.py`](./examples/5_get_content_of_projects.py): Inspecting project metadata.
- [`6_delete_projects.py`](./examples/6_delete_projects.py): Deleting projects.
- [`7_rename_project.py`](./examples/7_rename_project.py): Renaming projects.
- [`8_get_image_generation_history.py`](./examples/8_get_image_generation_history.py): Image generation history.
- [`9_save_images.py`](./examples/9_save_images.py): Generating and saving images.
- [`10_generate_image.py`](./examples/10_generate_image.py): Basic image generation.
- [`11_refine_image.py`](./examples/11_refine_image.py): Image refinement.

To run an example:
```bash
export WHISK_SESSION_COOKIE="your_whisk_session_cookie_here"
python whisk-api-python/examples/10_generate_image.py
```

## API Reference (Python Client)

The main interface is the `WhiskAPI` class in `whisk_api.client`.

### Core Methods

-   `WhiskAPI(session_cookie: str)`: Constructor, initializes the API client.
-   `get_authorization_token() -> str`: Fetches an authorization token.
-   `generate_image(request_data: GenerateImageRequest) -> GenerateImageResponse`: Generates images from prompts.
-   `refine_image(request_data: RefineImageRequest) -> GenerateImageResponse`: Refines existing images.
-   `get_project_history(limit: Optional[int] = None) -> List[ProjectHistoryItem]`: Retrieves project history.
-   `create_project(title: str) -> str`: Creates a new project and returns its ID.
-   `delete_projects(project_ids: List[str]) -> bool`: Deletes one or more projects.
-   `rename_project(project_id: str, new_name: str) -> str`: Renames a project.
-   `get_image_history(limit: Optional[int] = None) -> List[ImageHistoryItem]`: Retrieves image generation history.
-   `save_image(encoded_image_data: str, filename: str) -> bool`: Utility to save base64 encoded image data to a file.

### Request and Response Objects

-   Request parameters are typically passed as Pydantic models defined in `whisk_api.types` (e.g., `GenerateImageRequest`, `RefineImageRequest`).
-   Successful API responses are parsed into Pydantic models (e.g., `GenerateImageResponse`, `ProjectHistoryItem`).
-   If an API request fails (e.g., network error, bad status code like 4xx or 5xx), a `requests.exceptions.RequestException` (or a subclass) is raised.
-   If response parsing fails or input data is invalid, a `ValueError` (often a Pydantic `ValidationError`) might be raised.

Unlike the original TypeScript library's `Result<T>` type, this Python client follows common Python practices: successful data is returned directly, and errors are raised as exceptions.

## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-github-username/whisk-api-python.git
    cd whisk-api-python
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  **Install dependencies (including development tools):**
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure `requirements.txt` includes `pytest`, `requests`, `pydantic`).
    You might also want to install the package in editable mode for development:
    ```bash
    pip install -e .
    ```
4.  **Set up environment variables:**
    Export your session cookie as `WHISK_SESSION_COOKIE`:
    ```bash
    export WHISK_SESSION_COOKIE="whisk_session=YOUR_ACTUAL_COOKIE_VALUE"
    ```

## Testing

The test suite uses `pytest`. Ensure you have set the `WHISK_SESSION_COOKIE` environment variable as described in "Authentication" and "Development Setup".

To run tests:
```bash
python -m pytest
# or simply
pytest
```
Tests that make actual API calls are marked appropriately (e.g., `@pytest.mark.api_call`) and will be skipped by the `api_client` fixture in `conftest.py` if the cookie is not set.

## Limitations

-   Requires a valid Google Labs session cookie (`whisk_session`) for authentication.
-   The Whisk platform is experimental, and its API is unofficial and subject to change without notice. This library may break if the underlying API changes.
-   Regional availability of the Whisk platform may vary.
-   Rate limits or other usage restrictions on the API are unknown and not handled by this library beyond basic error reporting.

## Contributing

Contributions are welcome! Please ensure your code passes tests and adheres to the existing style. Consider opening an issue to discuss significant changes beforehand.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This is the same license as the original TypeScript library.

## Disclaimer

This is an unofficial API wrapper and is not affiliated with Google or the Google Labs team. Use at your own risk and ensure your usage complies with Google's terms of service for the Whisk platform. The maintainers of this Python wrapper are not responsible for any misuse or consequences of using this library.
