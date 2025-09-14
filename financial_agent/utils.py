from financial_agent.dataclass import UserDetails


def parse_user_details(data: dict) -> UserDetails:
    """
    Parses a dictionary into an instance of UserDetails.

    Args:
        data (dict): The dictionary containing user details.

    Returns:
        UserDetails: An instance of the UserDetails dataclass.
    """
    return UserDetails(
        user_id=data.get("user_id"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=data.get("email"),
        mobile=data.get("mobile"),
        device_id=data.get("device_id"),
        token_id=data.get("token_id"),
        role_type_mark=data.get("role_type_mark"),
    )
