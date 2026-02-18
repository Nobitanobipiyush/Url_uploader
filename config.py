import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")

    VIP_USERS = list(map(int, os.getenv("VIP_USERS", "").split())) if os.getenv("VIP_USERS") else []
