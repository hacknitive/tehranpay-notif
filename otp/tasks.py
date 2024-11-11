# otp/tasks.py

from celery import shared_task
from django.conf import settings
import time

@shared_task
def send_otp_task(phone_number, otp):
    # Simulate calling SMS provider API
    print(f"<<<<<<<<<<<<<<<<<Sending OTP {otp} to phone number {phone_number}>>>>>>>>>>>>>>>>>")
    # Example: time.sleep to simulate network delay
    time.sleep(2)
    # Log or handle success/failure accordingly