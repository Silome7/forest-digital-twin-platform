import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/DTDB"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "pass123")
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = False
