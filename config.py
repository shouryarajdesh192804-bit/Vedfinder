# =========================================
# VedFinder V2
# config.py
# =========================================

import os

from dotenv import load_dotenv


# =========================================
# Load .env
# =========================================

load_dotenv()


class Config:

    # -----------------------------------------
    # Flask
    # -----------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "vedfinder-development-secret"
    )

    DEBUG = (
        os.getenv(
            "FLASK_DEBUG",
            "false"
        ).lower()
        == "true"
    )

    # -----------------------------------------
    # YouTube
    # -----------------------------------------

    YOUTUBE_API_KEY = os.getenv(
        "YOUTUBE_API_KEY",
        ""
    )

    # -----------------------------------------
    # Google Maps
    # -----------------------------------------

    GOOGLE_MAPS_API_KEY = os.getenv(
        "GOOGLE_MAPS_API_KEY",
        ""
    )

    # -----------------------------------------
    # Google Discovery
    # -----------------------------------------

    GOOGLE_DISCOVERY_API_KEY = os.getenv(
        "GOOGLE_DISCOVERY_API_KEY",
        ""
    )

    # -----------------------------------------
    # Email / Gmail
    # -----------------------------------------

    EMAIL_USER = os.getenv(
        "EMAIL_USER",
        ""
    )

    EMAIL_PASSWORD = os.getenv(
        "EMAIL_PASSWORD",
        ""
    )

    # -----------------------------------------
    # Google AdSense
    # -----------------------------------------

    ADSENSE_CLIENT_ID = os.getenv(
        "ADSENSE_CLIENT_ID",
        ""
    )

    ADSENSE_SLOT_ID = os.getenv(
        "ADSENSE_SLOT_ID",
        ""
    )
    # =========================================
# VedFinder V2
# config.py
# =========================================

import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    # -----------------------------------------
    # Flask
    # -----------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "vedfinder-development-key"
    )

    DEBUG = os.getenv(
        "FLASK_DEBUG",
        "False"
    ).lower() == "true"


    # -----------------------------------------
    # YouTube
    # -----------------------------------------

    YOUTUBE_API_KEY = os.getenv(
        "YOUTUBE_API_KEY",
        ""
    )

    # -----------------------------------------
    # Email / OTP
    # -----------------------------------------

    EMAIL_USER = os.getenv(
        "EMAIL_USER",
        ""
    )

    EMAIL_PASSWORD = os.getenv(
        "EMAIL_PASSWORD",
        ""
    )


    # -----------------------------------------
    # Google AdSense
    # -----------------------------------------

    ADSENSE_CLIENT_ID = os.getenv(
        "ADSENSE_CLIENT_ID",
        ""
    )

    ADSENSE_SLOT_ID = os.getenv(
        "ADSENSE_SLOT_ID",
        ""
    )