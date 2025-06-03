import pytest
import time
# WhiskAPI provided by fixture. Types might be imported if needed for explicit type hints
# that aren't resolved via fixture.
# from whisk_api import WhiskAPI
from whisk_api.types import GenerateImageRequest, RefineImageRequest, GenerateImageResponse
from requests.exceptions import RequestException

# Helper function to validate image generation response structure
def validate_gen_response(response: GenerateImageResponse, expected_prompt_substring: str = None):
    assert response is not None, "API response should not be None"
    assert isinstance(response, GenerateImageResponse), "Response should be a GenerateImageResponse object"
    assert response.image_panels is not None, "Response should have 'image_panels'"
    assert len(response.image_panels) > 0, "'image_panels' list should not be empty"

    panel = response.image_panels[0]
    assert panel.generated_images is not None, "Image panel should have 'generated_images'"
    assert len(panel.generated_images) > 0, "'generated_images' list should not be empty"
    if expected_prompt_substring: # The prompt in response might be slightly modified by backend
        assert expected_prompt_substring.lower() in panel.prompt.lower(), f"Expected prompt substring '{expected_prompt_substring}' not in panel prompt '{panel.prompt}'"

    image = panel.generated_images[0]
    assert image.encoded_image is not None, "Generated image should have 'encoded_image' data"
    assert len(image.encoded_image) > 100, "Encoded image data seems too short" # Arbitrary check for some content
    assert image.media_generation_id is not None, "Generated image should have 'media_generation_id'"
    assert len(image.media_generation_id) > 0, "'media_generation_id' should not be empty"
    assert image.seed is not None, "Generated image should have a 'seed'"
    # image.prompt in GeneratedImage might also be checked if present


@pytest.mark.api_call
def test_generate_image_simple_prompt(api_client): # Type hint :WhiskAPI
    """Tests image generation with a simple prompt."""
    timestamp = int(time.time())
    prompt = f"A test cat playing with pytest logo - {timestamp}"
    print(f"Testing generate_image with prompt: {prompt}")

    request_data = GenerateImageRequest(prompt=prompt)

    try:
        response = api_client.generate_image(request_data)
        validate_gen_response(response, expected_prompt_substring="test cat")
        print(f"Generated image with media ID: {response.image_panels[0].generated_images[0].media_generation_id}")
    except RequestException as e:
        pytest.fail(f"API request failed during generate_image (simple prompt): {e}")
    except ValueError as e:
        pytest.fail(f"Value error (parsing) during generate_image (simple prompt): {e}")

@pytest.mark.api_call
def test_generate_image_with_seed(api_client): # Type hint :WhiskAPI
    """Tests image generation with a prompt and a specific seed."""
    timestamp = int(time.time())
    prompt = f"A test dog fetching a test stick, seeded - {timestamp}"
    seed = 123456789
    print(f"Testing generate_image with prompt: {prompt}, seed: {seed}")

    request_data = GenerateImageRequest(prompt=prompt, seed=seed)

    try:
        response = api_client.generate_image(request_data)
        validate_gen_response(response, expected_prompt_substring="test dog")
        # It's hard to assert the seed was *used* without visual inspection or more detailed API response,
        # but we can check if the response seed field matches if the API echoes it.
        # The current 'GeneratedImage' model has a 'seed' field from the response.
        assert response.image_panels[0].generated_images[0].seed == seed, \
            f"Response seed {response.image_panels[0].generated_images[0].seed} does not match requested seed {seed}"
        print(f"Generated image with seed, media ID: {response.image_panels[0].generated_images[0].media_generation_id}")
    except RequestException as e:
        pytest.fail(f"API request failed during generate_image (with seed): {e}")
    except ValueError as e:
        pytest.fail(f"Value error (parsing) during generate_image (with seed): {e}")


@pytest.mark.api_call
def test_refine_image(api_client): # Type hint :WhiskAPI
    """Tests image refinement based on an initially generated image."""
    timestamp = int(time.time())
    initial_prompt = f"A basic landscape for refinement test - {timestamp}"
    print(f"Testing refine_image. First, generating base image with prompt: {initial_prompt}")

    gen_request_data = GenerateImageRequest(prompt=initial_prompt, image_model="IMAGEN_3") # Specify model for consistency

    try:
        gen_response = api_client.generate_image(gen_request_data)
        validate_gen_response(gen_response, expected_prompt_substring="basic landscape")

        initial_image_details = gen_response.image_panels[0].generated_images[0]
        initial_image_id = initial_image_details.media_generation_id
        initial_encoded_image = initial_image_details.encoded_image
        # Use the prompt from the response for existing_prompt, as it might be altered by the backend
        base_prompt_for_refine = gen_response.image_panels[0].prompt

        print(f"Base image generated. Media ID: {initial_image_id}. Now refining...")

        refinement_instruction = "Add a bright red barn to the landscape."
        refine_request_data = RefineImageRequest(
            existing_prompt=base_prompt_for_refine,
            new_refinement=refinement_instruction,
            base64_image=initial_encoded_image,
            image_id=initial_image_id,
            image_model=initial_image_details.image_model or "IMAGEN_3", # Use model from generated image
            seed=initial_image_details.seed # Optionally reuse seed or use a new one
        )

        refine_response = api_client.refine_image(refine_request_data)
        # The refined prompt in the response might be a combination or just the new_refinement
        validate_gen_response(refine_response, expected_prompt_substring="red barn") # Check if refinement is in new prompt

        refined_image_details = refine_response.image_panels[0].generated_images[0]
        assert refined_image_details.media_generation_id != initial_image_id, \
            "Refined image should have a new media_generation_id"
        print(f"Image refined successfully. New media ID: {refined_image_details.media_generation_id}")

    except RequestException as e:
        pytest.fail(f"API request failed during refine_image test: {e}")
    except ValueError as e:
        pytest.fail(f"Value error (parsing) during refine_image test: {e}")
    except AssertionError as e:
        pytest.fail(f"Assertion failed during refine_image test: {e}")

# pytest.ini content for the marker:
# [pytest]
# markers =
#     api_call: marks tests that make real API calls
#     smoke: for basic smoke tests (like availability)
