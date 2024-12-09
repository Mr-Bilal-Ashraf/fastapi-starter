from dotenv import load_dotenv

import os


load_dotenv()


class Settings():
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1")

    APP_TITLE: str = os.getenv("APP_TITLE")
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION")
    APP_SUMMARY: str = os.getenv("APP_SUMMARY")
    APP_VERSION: str = os.getenv("APP_VERSION")
    APP_TERM_OF_SERVICE: str = os.getenv("APP_TERM_OF_SERVICE")
    APP_CONTACT_NAME: str = os.getenv("APP_CONTACT_NAME")
    APP_CONTACT_URL: str = os.getenv("APP_CONTACT_URL")
    APP_CONTACT_EMAIL: str = os.getenv("APP_CONTACT_EMAIL")
    APP_LICENSE_NAME: str = os.getenv("APP_LICENSE_NAME")
    APP_LICENSE_IDENTIFIER: str = os.getenv("APP_LICENSE_IDENTIFIER")

    MAILJET_API_PUB: str = os.getenv("MAILJET_API_PUB")
    MAILJET_API_PRI: str = os.getenv("MAILJET_API_PRI")
    MAILJET_SENDER_EMAIL: str = os.getenv("MAILJET_SENDER_EMAIL")
    MAILJET_SENDER_NAME: str = os.getenv("MAILJET_SENDER_NAME")

    ACCESS_TOKEN_EXPIRE: int = int(os.getenv("ACCESS_TOKEN_EXPIRE", 1))
    REFRESH_TOKEN_EXPIRE: int = int(os.getenv("ACCESS_TOKEN_EXPIRE", 30))


settings = Settings()
