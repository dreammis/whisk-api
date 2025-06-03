import requests
from typing import Optional, Dict, Any # For type hinting

DEFAULT_TIMEOUT = 30  # seconds

def make_request(
    url: str,
    method: str,
    headers: Optional[Dict[str, str]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> dict:
    """
    Makes an HTTP request to the specified URL with a default timeout.

    Args:
        url: The URL to make the request to.
        method: The HTTP method to use (e.g., "GET", "POST").
        headers: A dictionary of headers to include in the request.
        json_payload: A dictionary to send as JSON in the request body.
        query_params: A dictionary of query parameters to append to the URL.
        timeout: Timeout in seconds for the request.

    Returns:
        A dictionary representing the JSON response from the server.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the request.
    """
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            json=json_payload,
            params=query_params,
            timeout=timeout
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        # You can log the error here if needed
        # print(f"Error making request: {e}")
        raise e
    except ValueError: # Handle cases where response is not JSON (e.g., if raise_for_status passes but content isn't JSON)
        # This case is less likely if raise_for_status() is effective and API guarantees JSON for success,
        # but good as a safeguard.
        raise requests.exceptions.RequestException("Response was not valid JSON.")

if __name__ == '__main__':
    # Example Usage (replace with actual test cases or remove)
    try:
        # Example GET request
        get_url = "https://jsonplaceholder.typicode.com/todos/1"
        print(f"Making GET request to {get_url}")
        get_response = make_request(get_url, "GET")
        print("GET Response:", get_response)
        print("-" * 20)

        # Example POST request
        post_url = "https://jsonplaceholder.typicode.com/posts"
        post_payload = {"title": "foo", "body": "bar", "userId": 1}
        print(f"Making POST request to {post_url} with payload {post_payload}")
        post_response = make_request(post_url, "POST", json_payload=post_payload)
        print("POST Response:", post_response)
        print("-" * 20)

        # Example error handling for a non-existent URL
        error_url = "https://jsonplaceholder.typicode.com/non_existent_endpoint"
        print(f"Making GET request to {error_url} (expecting an error)")
        make_request(error_url, "GET")

    except requests.exceptions.RequestException as err:
        print(f"Request failed as expected: {err}")
    except Exception as general_err:
        print(f"An unexpected error occurred: {general_err}")
