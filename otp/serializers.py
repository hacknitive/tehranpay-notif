import re

from django.core.validators import RegexValidator
from rest_framework import serializers

# Constants for phone number validation
PHONE_REGEX_PATTERN = r"^\+98\d{10}$"
PHONE_NUMBER_MESSAGE = "Phone number must start with +98 followed by exactly 10 digits."
PHONE_NUMBER_CODE = "invalid_phone_number"


# Precompiled regex for performance optimization
PHONE_REGEX = re.compile(PHONE_REGEX_PATTERN)

# Reusable phone number validator
phone_number_validator = RegexValidator(
    regex=PHONE_REGEX,
    message=PHONE_NUMBER_MESSAGE,
    code=PHONE_NUMBER_CODE,
)


class PhoneNumberSerializer(serializers.Serializer):
    """Base serializer containing a validated phone number."""

    phone_number = serializers.CharField(validators=[phone_number_validator])


class SendOTPSerializer(PhoneNumberSerializer):
    """Serializer for sending OTP to a phone number."""

    # Inherits phone_number field from PhoneNumberSerializer
    pass


class VerifyOTPSerializer(PhoneNumberSerializer):
    """Serializer for verifying OTP for a phone number."""

    otp = serializers.CharField(
        max_length=6,
        min_length=4,
        required=True,
        help_text="One-Time Password sent to the user's phone number.",
    )

    def validate_otp(self, value):
        """
        Validate the OTP format.

        Args:
            value (str): The OTP provided by the user.

        Returns:
            str: The validated OTP.

        Raises:
            serializers.ValidationError: If the OTP does not meet the criteria.
        """
        if not value.isdigit():
            raise serializers.ValidationError("OTP must consist of digits only.")
        return value