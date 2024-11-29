"""Class to capture the login mechanics."""

import logging
from requests import Response, Session
import src.settings as setting

def get_login_response() -> Response:
    # Start a session
    session = Session()

    # Use the custom CA certificate for requests
    session.verify = setting.verify

    # Step 1: Get login token
    params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    }
    response = session.get(url=setting.api_url, params=params)
    login_token = response.json()['query']['tokens']['logintoken']

    # Step 2: Log in
    params = {
        'action': 'login',
        'lgname': setting.username,
        'lgpassword': setting.password,
        'lgtoken': login_token,
        'format': 'json'
    }

    response = session.post(url=setting.api_url, data=params)

    return response


def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Enable logging for requests
    logging.getLogger('urllib3').setLevel(logging.DEBUG)

    response = get_login_response()

    # Check if login was successful
    if response.json()['login']['result'] == 'Success':
        print("Logged in successfully!")
    else:
        print("Login failed:", response.json())
