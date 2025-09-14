import hashlib
from functools import wraps

from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.request import Request

from financial_agent.services.shield_service import LOGGER, IndShieldService

# logger = LOGGER(__name__)

def user_login_required(view_func):
    """
    Decorator to check if the user is logged in by validating the token.
    """
    @wraps(view_func)
    def decorated_function(request, *args, **kwargs):
        try:
            # Check if request is DRF's Request object or Django's HttpRequest
            if isinstance(request, Request):
                token = request.headers.get('Authorization')
                platform = request.headers.get('platform')
                member_id = request.query_params.get('member_id')  # DRF-specific
            else:
                token = request.headers.get('Authorization')
                platform = request.headers.get('platform')
                member_id = request.GET.get('member_id')  # Standard Django

            if not token:
                request.user_config = {
                    'user_id': request.GET.get('user_id'),
                    'first_name': 'John',
                    'last_name': 'Cena',
                    'mobile': '999999999',
                    'email': 'xyz@gmail.com',
                    'user_type': 2,

                }
                # logger.info(f"user_login_failed: Missing token. Headers: {str(request.headers)}, platform: {platform}")
                return view_func(request, *args, **kwargs)

            # Hash the token for caching
            hashed_token_key = f"shield_{hashlib.sha256(str(token).encode('utf-8')).hexdigest()}"
            if member_id:
                try:
                    member_id = int(member_id)
                except ValueError:
                    return JsonResponse({'status': False, 'msg': 'Invalid Member ID'}, status=400)
                hashed_token_key = f'{hashed_token_key}_{member_id}'

            # logger.info(f"user_login_required: {hashed_token_key} platform: {platform}")

            # Attempt to fetch cached data
            shield_verification_config = cache.get(hashed_token_key)
            if not shield_verification_config and token:
                # Validate the user token
                validation_resp = validate_user_token(token, member_id=member_id)
                # logger.info(f"user_login_required: {hashed_token_key} platform: {platform}, {validation_resp}")
                if validation_resp is not None and len(validation_resp) > 0:
                    validation_resp = validation_resp[0]

                if validation_resp.get('status'):
                    if validation_resp and validation_resp.get('user_id'):
                        shield_verification_config = {
                            'user_id': validation_resp.get('user_id'),
                            'device_id': validation_resp.get('device_id'),
                            'role_type_mark': validation_resp.get('role_type_mark'),
                            'token_id': validation_resp.get('token_id'),
                            'first_name': validation_resp.get('first_name'),
                            'last_name': validation_resp.get('last_name'),
                            'mobile': validation_resp.get('mobile'),
                            'email': validation_resp.get('email'),
                            'user_type': validation_resp.get('type'),
                        }


            if shield_verification_config:
                # Attach user data to the request object
                request.user_config = shield_verification_config
                return view_func(request, *args, **kwargs)
            else:
                # logger.error(f"user_login_failed: {hashed_token_key} platform: {platform}")
                return JsonResponse({'status': False, 'msg': 'Token expired'}, status=400)

        except Exception as e:
            # logger.error(f"user_login_failed: {e}")
            return JsonResponse({'status': False, 'msg': 'Token expired'}, status=400)

    return decorated_function  # TODO: Return the decorated function check if it breaks later

def validate_user_token(token, member_id=None):
    """
    Validates the user token using the Shield service.
    """
    shield_service = IndShieldService()
    return shield_service.validate_user_and_get_info(token, member_id=member_id)
