import requests
from requests.auth import HTTPBasicAuth


class DataService:
    def __init__(self, user_id):
        self.user_id = user_id

    def user_details(self):
        """
        Fetches user details from the specified API.

        Returns:
            dict: The user profile details or error information.
        """
        # API endpoint
        url = f"https://profilex-int.indiawealth.in/private/v1/user/profile/by_dimension/user_id/{self.user_id}/?key="

        # Basic auth credentials
        auth = HTTPBasicAuth("profilex", "P8gd.}Q.~JbgmV/t")

        try:
            # Send GET request
            response = requests.get(url, auth=auth)

            # Raise exception if the response indicates an HTTP error
            response.raise_for_status()

            # Parse JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle HTTP or connection errors
            return {"status": "error", "message": str(e)}

    def aggregated_holdings(self):
        """curl --location 'https://ind-memory.indiawealth.in/v1/holdings/aggregate/' \
            --header 'Content-Type: application/json' \
            --header 'Content-Encoding: application/gzip' \
            --data '{
                "users":["1823308"]
                "group_by":["asset_type"]
            }'"""

        response = requests.post(
            'https://ind-memory.indiawealth.in/v1/holdings/aggregate/',
            headers={
                'Content-Type': 'application/json',
                'Content-Encoding': 'application/gzip'
            },
            json={
                'users': [self.user_id],
                'group_by': ['asset_type']
            }
        )

        return response.json()

    def user_holdings(self):
        """
        curl --location 'https://ind-memory.indiawealth.in/v1/holdings/' \
        --header 'Content-Type: application/json' \
        --header 'Content-Encoding: application/gzip' \
        --data '{
            "users": ["1246621"],
            "query": {
                    "filters": {
                    "asset_type": {
                            "in":["US_Stock"]
                    }
                    }
                }
        }'

        Asset Types
        ASSET_TYPE_INSURANCE = "INSURANCE"
        ASSET_TYPE_MINI_SAVE = "MINI_SAVE"
        ASSET_TYPE_STOCK     = "STOCK"
        ASSET_TYPE_MF       = "MF"
        ASSET_TYPE_US_STOCK = "US_STOCK"
        ASSET_TYPE_NPS      = "NPS"
        ASSET_TYPE_FD       = "FD"
        ASSET_TYPE_RE       = "RE"
        ASSET_TYPE_BOND     = "BOND"
        ASSET_TYPE_OI       = "OI"
        ASSET_TYPE_RD       = "RD"
        ASSET_TYPE_AIF      = "AIF"
        ASSET_TYPE_PMS      = "PMS"
        ASSET_TYPE_SA       = "SA"
        ASSET_TYPE_EPF      = "EPF"
        ASSET_TYPE_PPF      = "PPF"
        """

        responses = {}

        asset_types = ["INSURANCE", "MINI_SAVE", "STOCK", "MF", "US_STOCK", "NPS", "FD", "RE", "BOND", "OI", "RD",
                       "AIF", "PMS", "SA", "EPF", "PPF"]
        for asset_type in asset_types:
            response = requests.post(
                'https://ind-memory.indiawealth.in/v1/holdings/',
                headers={
                    'Content-Type': 'application/json',
                    'Content-Encoding': 'application/gzip'
                },
                json={
                    'users': [self.user_id],
                    'query': {
                        'filters': {
                            'asset_type': {
                                'in': [asset_type]
                            }
                        }
                    }
                }
            )
            if response.json():
                responses[asset_type] = response.json()
        return responses

    def mf_portfolio_data(self):
        response = requests.post(
            'https://ind-memory.indiawealth.in/v1/holdings/',
            headers={
                'Content-Type': 'application/json',
                'Content-Encoding': 'application/gzip'
            },
            json={
                'users': [str(self.user_id)],
                'query': {
                    'filters': {
                        'asset_type': {
                            'in': ['MF']
                        }
                    }
                }
            }
        )
        # print(response.json())
        if response.ok:
            return response.json()['data']['results']
        return {}

    def invested_mf_fund_info(self):

        fund_data = {}
        response = requests.get(
            f"https://mf-tracking.indiawealth.in/v2/users/{self.user_id}/portfolio/funds/?response_format=json")
        
        holdings_data = response.json()

        if not holdings_data["success"]:
            raise requests.exceptions.HTTPError(f"failed to fetch user holdings for the given user-id: {self.user_id} ")
        
        parsed_holdings_data = {}

        for fund in holdings_data["data"]["funds"]:
            parsed_holdings_data[fund["fundDetails"]["name"]] = fund

        return parsed_holdings_data


    def user_portfolio_information(self):
        response = requests.get(
            f"http://indian-stock-broker.internal.indmoney.com/internal/portfolio/broker-summary?segment=cash&app_version=7.5.2&platform=android&response_format=json&user_id={self.user_id}")
        if not response.ok:
            return {}
        data = response.json()['summary']
        response_data = {}

        for broker in data:
            if not broker["broker_asset_summary"] or not broker["broker_asset_summary"]["holdings_summary"]:
                continue

            response_data["summary"] = broker["broker_asset_summary"]["holdings_summary"]
            response_data["investments"] = broker["broker_asset_summary"]["scrip_details"]

        return response_data
    
    
    def mutual_fund_insight(self, fund_id):
        response = requests.get(f"https://mf-tracking.indiawealth.in/v1/funds/{fund_id}/?dump=true")
        if not response.ok:
            return {}
        
        data = response.json()['summary']

        response_data = {
            "fund_name": data["keys"]["name"],
            "risk_measures": data["keys"]["risk_measures"]
        }

        if data["keys"]["conc_analysis"]:
            response_data["analysis"] = data["keys"]["conc_analysis"][0]

        return response_data
        



