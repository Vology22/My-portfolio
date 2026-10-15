import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.group_token = os.environ["GROUP_TOKEN"]
        self.group_id = int(os.environ["GROUP_ID"])
        self.admin_ids = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]
        self.db_path = os.environ.get("DB_PATH", "bot.db")


settings = Settings()
