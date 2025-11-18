from dotenv import load_dotenv
import os


def load_secrets():
    """Load secrets from .env file into environment variables."""
    load_dotenv()

def get_secret(key: str) -> str:
    """Retrieve a secret value from environment variables."""
    value = os.getenv(key)
    if value is None:
        return None
    return value