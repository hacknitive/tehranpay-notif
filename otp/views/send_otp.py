import random

from rest_framework import generics, status
from rest_framework.response import Response

from ..serializers import SendOTPSerializer
from ..tasks import send_otp_task
from utils import redis_client_ins

# Constants for OTP generation and response messages
OTP_LENGTH = 6
OTP_MIN_VALUE = 10**(OTP_LENGTH - 1)
OTP_MAX_VALUE = (10**OTP_LENGTH) - 1

SUCCESS_MESSAGE = "OTP sent successfully."
STATUS_CODE_SUCCESS = status.HTTP_200_OK


def generate_otp(length=OTP_LENGTH):
    """
    Generates a random One-Time Password (OTP) of specified length.

    Args:
        length (int): The length of the OTP to generate. Defaults to OTP_LENGTH.

    Returns:
        str: A string representing the generated OTP.
    """
    return str(random.randint(OTP_MIN_VALUE, OTP_MAX_VALUE))


class SendOTPView(generics.GenericAPIView):
    """API view to handle the sending of One-Time Passwords (OTP) to users."""

    serializer_class = SendOTPSerializer

    def post(self, request):
        """
        Handles POST requests to send an OTP to the provided phone number.

        Validates the input data, generates an OTP, stores it in Redis,
        and triggers an asynchronous task to send the OTP via SMS.

        Args:
            request (HttpRequest): The incoming HTTP request containing the phone number.

        Returns:
            Response: A JSON response indicating the success or failure of the OTP sending process.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp = generate_otp()

        self.store_otp(phone_number, otp)
        self.dispatch_send_otp_task(phone_number, otp)

        return self.success_response()

    def store_otp(self, phone_number, otp):
        """
        Stores the generated OTP in Redis with a predefined Time-To-Live (TTL).

        Args:
            phone_number (str): The user's phone number.
            otp (str): The generated OTP to store.
        """
        redis_client_ins.set_otp(phone_number=phone_number, otp_code=otp)

    def dispatch_send_otp_task(self, phone_number, otp):
        """
        Dispatches an asynchronous task to send the OTP via SMS.

        Args:
            phone_number (str): The user's phone number.
            otp (str): The OTP to send.
        """
        send_otp_task.delay(phone_number, otp)

    def success_response(self):
        """
        Constructs a standardized success JSON response.

        Returns:
            Response: A DRF Response object with the success message and HTTP 200 status.
        """
        response_data = {
            "statusCode": STATUS_CODE_SUCCESS,
            "message": SUCCESS_MESSAGE,
            "error": None,
            "data": None,
        }
        return Response(response_data, status=STATUS_CODE_SUCCESS)