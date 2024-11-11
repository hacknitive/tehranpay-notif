from traceback import print_exc

from requests import post
from django.conf import settings
from django.http import JsonResponse
from pybreaker import (
    CircuitBreaker,
    CircuitBreakerError,
)
from jwt import (
    InvalidTokenError,
    ExpiredSignatureError,
)

from utils import (
    extract_token,
    decode_token,
)


class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize Circuit Breaker
        self.circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse(
                {
                    "statusCode": 401,
                    "message": "Operation failed.",
                    "error": "Authorization header missing.",
                    "data": None,
                },
                status=401,
            )

        try:
            token = extract_token(auth_header=auth_header)
            payload = decode_token(token=token)

            token_type = payload.get("type")
            if token_type != "access":
                return JsonResponse(
                    {
                        "statusCode": 401,
                        "message": "Operation failed.",
                        "error": "Invalid token.",
                        "data": None,
                    },
                    status=401,
                )

            response = self.circuit_breaker.call(
                post, settings.TOKEN_VALIDATION_URL, json={"token": token}
            )

            jsoned_response = response.json()
            if response.status_code == 200 and jsoned_response["data"]["is_valid"]:
                return self.get_response(request)
            else:
                print(str(response.text))
                return JsonResponse(
                    {
                        "statusCode": 401,
                        "message": "Operation failed.",
                        "error": "Invalid token.",
                        "data": None,
                    },
                    status=401,
                )

        except ExpiredSignatureError:
            return JsonResponse(
                {
                    "statusCode": 401,
                    "message": "Operation failed.",
                    "error": "Token has expired.",
                    "data": None,
                },
                status=401,
            )
        except InvalidTokenError:
            return JsonResponse(
                {
                    "statusCode": 401,
                    "message": "Operation failed.",
                    "error": "Invalid token.",
                    "data": None,
                },
                status=401,
            )
        except CircuitBreakerError:
            return JsonResponse(
                {
                    "statusCode": 401,
                    "message": "Operation failed.",
                    "error": "Authentication Service unavailable.",
                    "data": None,
                },
                status=401,
            )
        except Exception:
            print(str(response.text))
            # TODO: Logging
            print_exc()
            return JsonResponse(
                {
                    "statusCode": 500,
                    "message": "Operation failed.",
                    "error": "Token validation failed.",
                    "data": None,
                },
                status=401,
            )
