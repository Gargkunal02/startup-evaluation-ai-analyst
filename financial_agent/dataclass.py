from dataclasses import dataclass
from typing import Optional

@dataclass
class UserDetails:
    user_id: int
    device_id: Optional[str] = None
    role_type_mark: Optional[int] = None
    token_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None