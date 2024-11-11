from rest_framework import serializers
from django.core.validators import RegexValidator

REGEX_PATTERN = r"^\+98\d{10}$"
MESSAGE = "Phone number must start with +98 followed by exactly 10 digits."
CODE = "invalid_phone_number"


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=REGEX_PATTERN,
                message=MESSAGE,
                code=CODE,
            ),
        ]
    )


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=REGEX_PATTERN,
                message=MESSAGE,
                code=CODE,
            ),
        ]
    )
    otp = serializers.CharField()
