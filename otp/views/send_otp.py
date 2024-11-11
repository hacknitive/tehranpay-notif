from random import randint

from rest_framework import generics, status
from rest_framework.response import Response
from ..serializers import SendOTPSerializer
from ..tasks import send_otp_task
from utils import redis_client_ins


class SendOTPView(generics.GenericAPIView):
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # Generate OTP (e.g., 6-digit)
        otp = self.generate_otp()

        # Store OTP in Redis with TTL
        redis_client_ins.set_otp(phone_number=phone_number, otp_code=otp)

        # Trigger async task to send OTP via SMS
        send_otp_task.delay(phone_number, otp)

        return Response(
            {
                "statusCode": status.HTTP_200_OK,
                "message": "OTP sent successfully.",
                "error": None,
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    def generate_otp(self):
        return f"{randint(100000, 999999)}"
