import pyotp


def generated_totp_secret():
    return pyotp.random_base32()


def verify_totp(totp_secret: str, code: str):
    return pyotp.TOTP(totp_secret).verify(code)
