from rest_framework import generics, status
from rest_framework.response import Response
from ..serializers import VerifyOTPSerializer
from utils import redis_client_ins


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

        # Retrieve OTP from Redis
        stored_otp = redis_client_ins.get_otp(phone_number=phone_number)
        if stored_otp is None:
            return Response(
                {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Operation failed.",
                    "error": "OTP has expired or does not exist.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if stored_otp.decode('utf-8') == otp:
            # Delete OTP after successful verification
            redis_client_ins.delete_otp(phone_number=phone_number)
            return Response(
                {
                    "statusCode": status.HTTP_200_OK,
                    "message": "OTP verified successfully.",
                    "error": None,
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Operation failed.",
                    "error": "Invalid OTP.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
