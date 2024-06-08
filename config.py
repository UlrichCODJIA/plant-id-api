import os
from flask import request
from dotenv import load_dotenv
from flask_limiter.util import get_remote_address

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    PLANTNET_API_KEY = os.environ.get("PLANTNET_API_KEY")
    PLANTNET_API_ENDPOINT = "https://my-api.plantnet.org/v2/identify/all"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    MAX_IMAGES = 5
    ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 3600
    RATELIMIT_DEFAULT = "10/minute"
    RATELIMIT_STORAGE_URI=os.environ.get("REDIS_URL")
    RATELIMIT_STRATEGY="fixed-window-elastic-expiry"
    RATELIMIT_HEADERS_ENABLED=True
    RATELIMIT_HEADER_LIMIT="X-My-RateLimit-Limit"
    RATELIMIT_HEADER_REMAINING="X-My-RateLimit-Remaining"
    RATELIMIT_HEADER_RESET="X-My-RateLimit-Reset"
    RATELIMIT_SWALLOW_ERRORS=False