import random

otp_storage = {}

def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    otp_storage[phone] = otp
    return otp

def verify_otp(phone: str, otp: str) -> bool:
    return otp_storage.get(phone) == otp
