from rest_framework import generics, status
from rest_framework.response import Response

from ..serializers import VerifyOTPSerializer
from utils import redis_client_ins


# Constants for response messages and status codes
STATUS_CODE_SUCCESS = status.HTTP_200_OK
STATUS_CODE_BAD_REQUEST = status.HTTP_400_BAD_REQUEST

MESSAGE_OPERATION_FAILED = "Operation failed."
MESSAGE_OTP_EXPIRED = "OTP has expired or does not exist."
MESSAGE_INVALID_OTP = "Invalid OTP."
MESSAGE_VERIFIED_SUCCESS = "OTP verified successfully."


def build_response(status_code, message, error=None, data=None):
    """
    Constructs a standardized JSON response.

    Args:
        status_code (int): The HTTP status code for the response.
        message (str): A message describing the outcome.
        error (str, optional): An error message if applicable. Defaults to None.
        data (dict, optional): Any additional data to include. Defaults to None.

    Returns:
        Response: A DRF Response object with the specified data and status.
    """
    return Response(
        {
            "statusCode": status_code,
            "message": message,
            "error": error,
            "data": data,
        },
        status=status_code,
    )


class VerifyOTPView(generics.GenericAPIView):
    """API view to handle the verification of One-Time Passwords (OTP) for users."""

    serializer_class = VerifyOTPSerializer

    def post(self, request):
        """
        Handles POST requests to verify an OTP for a provided phone number.

        Validates the input data, retrieves the stored OTP from Redis,
        compares it with the provided OTP, and responds accordingly.

        Args:
            request (HttpRequest): The incoming HTTP request containing the phone number and OTP.

        Returns:
            Response: A JSON response indicating the success or failure of the OTP verification process.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_provided = serializer.validated_data["otp"]

        stored_otp = self.retrieve_stored_otp(phone_number)
        if stored_otp is None:

            return build_response(
                status_code=STATUS_CODE_BAD_REQUEST,
                message=MESSAGE_OPERATION_FAILED,
                error=MESSAGE_OTP_EXPIRED,
            )

        if self.is_otp_valid(stored_otp, otp_provided):
            self.delete_stored_otp(phone_number)
            return build_response(
                status_code=STATUS_CODE_SUCCESS,
                message=MESSAGE_VERIFIED_SUCCESS,
            )
        else:
            return build_response(
                status_code=STATUS_CODE_BAD_REQUEST,
                message=MESSAGE_OPERATION_FAILED,
                error=MESSAGE_INVALID_OTP,
            )

    def retrieve_stored_otp(self, phone_number):
        """
        Retrieves the stored OTP from Redis for a given phone number.

        Args:
            phone_number (str): The user's phone number.

        Returns:
            bytes or None: The stored OTP as bytes if exists, else None.
        """
        try:
            return redis_client_ins.get_otp(phone_number=phone_number)
        except Exception:
            # TODO: Logging
            return None

    def is_otp_valid(self, stored_otp, provided_otp):
        """
        Compares the stored OTP with the provided OTP.

        Args:
            stored_otp (bytes): The OTP retrieved from Redis.
            provided_otp (str): The OTP provided by the user.

        Returns:
            bool: True if the OTPs match, False otherwise.
        """
        try:
            decoded_stored_otp = stored_otp.decode("utf-8")
            return decoded_stored_otp == provided_otp
        except UnicodeDecodeError:
            # TODO: Logging
            return False

    def delete_stored_otp(self, phone_number):
        """
        Deletes the stored OTP from Redis for a given phone number.

        Args:
            phone_number (str): The user's phone number.
        """
        try:
            redis_client_ins.delete_otp(phone_number=phone_number)
        except Exception:
            # TODO: Logging
            pass
