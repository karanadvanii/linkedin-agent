from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

class Settings:
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Google Sheets
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
)
    
    # RapidAPI
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

    # LinkedIn
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

    # Agent config
    POSTS_PER_RUN = 1
    SCHEDULE_DAYS = ["monday", "thursday"]  # twice a week
    SCHEDULE_TIME = "09:00"

settings = Settings()