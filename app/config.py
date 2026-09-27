import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY","change-this-secret-key")

    AI_API_KEY = os.environ.get("AI_API_KEY","")

    AI_MODEL = os.environ.get("AI_MODEL","")

    GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_TOKEN_FILE","token.json")

    GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID","primary")

    DATABASE_PATH = os.getenv("DATABASE_PATH","data.contacts.db")