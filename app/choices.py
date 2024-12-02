from enum import Enum


class OTPChoices(str, Enum):
    ACCOUNT_ACTIVATION = "activation"
    EMAIL_VERIFICATION = "email_veri"
    FORGOT_PASSWORD = "forgot_pass"
    TWO_FACTOR = "two_factor"
