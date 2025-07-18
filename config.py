import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///reklamaton.db") 