from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import os
# initialize logger
from utils import logs

load_dotenv()


@dataclass
class Credentials:
    SECRET: str
    KEY: str

    def __init__(self, SECRET: str, KEY: str):
        if not SECRET or not KEY:
            raise ValueError("SECRET and KEY must be set in .env file")
        self.SECRET = SECRET
        self.KEY = KEY


@dataclass
class RedisConfig:
    url: str
    port: str
    full_url: Optional[str] = None

    def __init__(self, url: str, port: str):
        if not url or not port:
            raise ValueError("REDIS_URL and REDIS_PORT must be set in .env file")
        self.url = url
        self.port = port
        self.full_url = f"redis://{self.url}:{self.port}"


@dataclass
class Settings:
    demo: bool = False

    def __init__(self, demo: bool):
        if isinstance(demo, str):
            self.demo = True if demo == "True" else False


CREDS = Credentials(SECRET=os.getenv("BROKER_SECRET"), KEY=os.getenv("BROKER_KEY"))
REDIS = RedisConfig(url=os.getenv("REDIS_URL"), port=os.getenv("REDIS_PORT"))
CONF = Settings(demo=os.getenv("DEMO"))
