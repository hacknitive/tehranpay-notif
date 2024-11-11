from traceback import print_exc

from redis import Redis as _Redis
from redis import (
    ConnectionPool,
    ConnectionError,
)
from django.conf import settings


class Redis(_Redis):

    def get_otp(self, phone_number: str):
        return self.get(name=f"otp:{phone_number}")

    def set_otp(
        self,
        phone_number: str,
        otp_code: str,
    ):
        return self.set(
            name=f"otp:{phone_number}",
            value=otp_code,
            ex=settings.OTP_TTL_SECONDS,
        )
    
    def delete_otp(
        self,
        phone_number: str,
    ):
        return self.delete(f"otp:{phone_number}")


class RedisClient:
    _instance: Redis = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance: Redis = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    connection_pool=ConnectionPool(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB,
                        password=settings.REDIS_PASSWORD,
                        max_connections=100,
                    ),
                )
                # Test connection
                cls._instance.ping()
            except ConnectionError:
                # TODO: Logging
                print_exc()
                cls._instance = None
        return cls._instance


redis_client_ins = RedisClient()

