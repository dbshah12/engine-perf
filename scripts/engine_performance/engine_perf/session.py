import requests

from .logger import logger


def initialize_api_session(base_url, username, password):
    session = requests.Session()
    session.verify = False  # Disable SSL certificate verification
    session.headers.update({"Content-Type": "application/json"})

    # Create API session
    session_endpoint = f"{base_url}/resources/json/delphix/session"
    session_payload = {
        "type": "APISession",
        "version": {"type": "APIVersion", "major": 1, "minor": 11, "micro": 41},
    }

    try:
        response = session.post(session_endpoint, json=session_payload)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to create API session: {e}")
        return None

    # Login
    login_endpoint = f"{base_url}/resources/json/delphix/login"
    login_payload = {"type": "LoginRequest", "username": username, "password": password}
    try:
        response = session.post(login_endpoint, json=login_payload)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Login failed: {e}")
        return None

    return session
