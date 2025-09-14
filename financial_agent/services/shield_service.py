from logging import Logger

import requests

LOGGER = Logger(__name__)


class IndShieldService:

    def __init__(self):
        self.base_url = "https://shield-int.indiawealth.in"
        self.user_validate_path = '/public/auth/v1/user/validate?key={}'
        self.auth_token = "cHJvZmlsZXg6UDhnZC59US5+SmJnbVYvdA=="
        self.profilex_service_key = "f4961c9d8dbe9d5d2d6dc48168b2b33dada4920f30832a16ba16d0ead2c8a3f04b"

    def validate_schema(self, data):
        """
        Validates the schema of the given data.
        """
        try:
            return data
        except Exception as err:
            LOGGER.error(message=str(err), bucket="VALIDATE_SCHEMA")
        return None

    def validate_user_info(self, resp):
        """
        Deprecated (moved to ProfilexService).
        Validates if user data is present in the response.
        """
        if 'data' in resp and resp['data']:
            return resp['data']
        LOGGER.error(message='Data not present in Ind Shield user info', bucket="USER_INFO")
        return None

    def validate_user_and_get_info(self, auth_token: str, member_id=None) -> (dict, str):
        """
        Validates the user and retrieves their information using an auth token.

        Args:
            auth_token (str): The user's authentication token.
            member_id (str, optional): The member ID, if applicable.

        Returns:
            tuple: A dictionary with the user's information and an error string, if any.
        """
        # Construct the URL
        url = f"{self.base_url}{self.user_validate_path.format(self.profilex_service_key)}"
        if member_id:
            url += f'&member_id={member_id}'

        headers = {
            'Authorization': auth_token,
            'platform': 'web'
        }

        try:
            # Make the POST request
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            # Parse response
            resp_data = response.json()
            if not resp_data.get('status'):
                LOGGER.error(message="Invalid response from Ind Shield API", bucket="USER_VALIDATE")
                return None, "Invalid response from Ind Shield API"

            return resp_data, ''
        except requests.exceptions.RequestException as e:
            # Handle exceptions and log errors
            LOGGER.error(message=f"Request error: {str(e)}", bucket="USER_VALIDATE")
            return None, str(e)
