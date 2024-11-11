from traceback import print_exc

from requests import post
from django.conf import settings
from django.http import JsonResponse
from pybreaker import CircuitBreaker, CircuitBreakerError
from jwt import ExpiredSignatureError, InvalidTokenError

from utils import extract_token, decode_token


# Constants for response messages and status codes
AUTHORIZATION_HEADER = "Authorization"
STATUS_UNAUTHORIZED = 401
STATUS_INTERNAL_SERVER_ERROR = 500

ERROR_RESPONSES = {
    "missing_authorization": {
        "statusCode": STATUS_UNAUTHORIZED,
        "message": "Operation failed.",
        "error": "Authorization header missing.",
        "data": None,
    },
    "invalid_token": {
        "statusCode": STATUS_UNAUTHORIZED,
        "message": "Operation failed.",
        "error": "Invalid token.",
        "data": None,
    },
    "expired_token": {
        "statusCode": STATUS_UNAUTHORIZED,
        "message": "Operation failed.",
        "error": "Token has expired.",
        "data": None,
    },
    "service_unavailable": {
        "statusCode": STATUS_UNAUTHORIZED,
        "message": "Operation failed.",
        "error": "Authentication Service unavailable.",
        "data": None,
    },
    "validation_failed": {
        "statusCode": STATUS_INTERNAL_SERVER_ERROR,
        "message": "Operation failed.",
        "error": "Token validation failed.",
        "data": None,
    },
}


def json_unauthorized_response(error_key):
    """Utility function to generate unauthorized JsonResponse."""
    response = ERROR_RESPONSES.get(error_key, ERROR_RESPONSES["validation_failed"])
    return JsonResponse(response, status=response["statusCode"])


class TokenValidationMiddleware:
    """Middleware for validating JWT tokens on specific API endpoints."""

    def __init__(self, get_response):
        """
        Initializes the middleware with the next callable in the chain.

        Args:
            get_response (callable): The next middleware or view.
        """
        self.get_response = get_response
        self.circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

    def __call__(self, request):
        """
        Processes the incoming HTTP request.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response.
        """
        if not request.path.startswith("/api/otp/"):
            return self.get_response(request)

        auth_header = request.headers.get(AUTHORIZATION_HEADER)
        if not auth_header:
            return json_unauthorized_response("missing_authorization")

        try:
            token = extract_token(auth_header=auth_header)
            payload = decode_token(token=token)

            if payload.get("type") != "access":
                return json_unauthorized_response("invalid_token")

            response = self.validate_token_with_service(token)

            if self.is_token_valid(response):
                return self.get_response(request)
            else:
                return json_unauthorized_response("invalid_token")

        except ExpiredSignatureError:
            return json_unauthorized_response("expired_token")
        except InvalidTokenError:
            return json_unauthorized_response("invalid_token")
        except CircuitBreakerError:
            return json_unauthorized_response("service_unavailable")
        except Exception:
            # TODO: Logging
            return JsonResponse(
                ERROR_RESPONSES["validation_failed"],
                status=STATUS_INTERNAL_SERVER_ERROR,
            )

    def validate_token_with_service(self, token):
        """
        Validates the token by calling the external authentication service.

        Args:
            token (str): The JWT token to validate.

        Returns:
            requests.Response: The response from the authentication service.
        """
        return self.circuit_breaker.call(
            post,
            settings.TOKEN_VALIDATION_URL,
            json={"token": token},
        )

    @staticmethod
    def is_token_valid(response):
        """
        Determines if the token is valid based on the authentication service response.

        Args:
            response (requests.Response): The response from the authentication service.

        Returns:
            bool: True if token is valid, False otherwise.
        """
        try:
            json_response = response.json()
            return response.status_code == 200 and json_response.get("data", {}).get("is_valid", False)
        except ValueError:
            # TODO: Logging
            return False