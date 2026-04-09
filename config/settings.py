from dotenv import load_dotenv
import os

load_dotenv()  # auto-discovers .env from project root


class Settings:
    # Author persona (customize in .env for your own voice)
    AUTHOR_NAME: str = os.getenv("AUTHOR_NAME", "Alex")
    AUTHOR_ROLE: str = os.getenv("AUTHOR_ROLE", "software engineer")
    AUTHOR_TOPICS: str = os.getenv("AUTHOR_TOPICS", "AI, software development, and tech trends")
    AUTHOR_AUDIENCE: str = os.getenv("AUTHOR_AUDIENCE", "tech-curious professionals aged 25-45")

    # Gemini
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # Telegram
    TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str | None = os.getenv("TELEGRAM_CHAT_ID")

    # Google Sheets
    GOOGLE_SHEET_ID: str | None = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_CREDENTIALS_PATH: str = os.getenv(
        "GOOGLE_CREDENTIALS_PATH",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
    )

    # RapidAPI
    RAPIDAPI_KEY: str | None = os.getenv("RAPIDAPI_KEY")

    # LinkedIn
    LINKEDIN_ACCESS_TOKEN: str | None = os.getenv("LINKEDIN_ACCESS_TOKEN")
    LINKEDIN_PERSON_URN: str | None = os.getenv("LINKEDIN_PERSON_URN")

    # Agent config
    POSTS_PER_RUN: int = 1
    SCHEDULE_DAYS: list[str] = ["monday", "thursday"]
    SCHEDULE_TIME: str = "09:00"

    REQUIRED_VARS: list[str] = [
        "GEMINI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "GOOGLE_SHEET_ID",
        "LINKEDIN_ACCESS_TOKEN",
        "LINKEDIN_PERSON_URN",
    ]

    def validate(self) -> None:
        missing = [v for v in self.REQUIRED_VARS if not getattr(self, v, None)]
        if missing:
            raise EnvironmentError(
                "\n❌ Missing required environment variables:\n"
                + "\n".join(f"  - {v}" for v in missing)
                + "\n\nCopy .env.example to .env and fill in the values."
            )


settings = Settings()