import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
  PROJECT_NAME: str = "Nexum AI: Secure Image Analyzer Agent"
  VERSION: str = "1.0.0"
  GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
  MODEL_NAME: str = "gemini-3.6-flash"


settings = Settings()