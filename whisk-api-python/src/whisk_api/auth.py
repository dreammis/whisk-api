class Authenticator:
    """
    Handles authentication for the Whisk API by storing the session cookie
    and providing headers for authenticated requests.
    """

    def __init__(self, session_cookie: str):
        """
        Initializes the Authenticator with the session cookie.

        Args:
            session_cookie: The session cookie string (e.g., "whisk_session=YOUR_COOKIE_VALUE").
        """
        if not session_cookie or not isinstance(session_cookie, str):
            raise ValueError("Session cookie must be a non-empty string.")
        self.session_cookie = session_cookie

    def get_auth_headers(self) -> dict:
        """
        Returns the headers required for making authenticated API requests.

        Returns:
            A dictionary containing the 'Cookie' header with the session cookie.
        """
        return {"Cookie": self.session_cookie}

if __name__ == '__main__':
    # Example Usage:
    try:
        # Valid cookie
        authenticator = Authenticator("whisk_session=somesessionid12345")
        headers = authenticator.get_auth_headers()
        print(f"Generated Headers: {headers}")
        assert headers == {"Cookie": "whisk_session=somesessionid12345"}
        print("Authenticator created and headers generated successfully.")

        # Example of invalid cookie (empty string)
        print("\nTesting with empty session cookie (expecting ValueError):")
        try:
            invalid_auth_empty = Authenticator("")
        except ValueError as e:
            print(f"Caught expected error: {e}")

        # Example of invalid cookie (not a string)
        print("\nTesting with non-string session cookie (expecting ValueError):")
        try:
            invalid_auth_type = Authenticator(12345)
        except ValueError as e:
            print(f"Caught expected error: {e}")

    except ValueError as ve:
        print(f"Error during example: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during example: {e}")
