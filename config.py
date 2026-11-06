import os
import sys

from dotenv import load_dotenv

# Load variables from .env into the environment (existing env vars take precedence)
load_dotenv()

DEV_SECRET_KEY = "dev-only-insecure-secret-key"


def _require(name):
    """ Return a required environment variable, or exit with a clear message if missing. """
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(
            f"❌ {name} is not set. Copy .env.example to .env and set {name}, "
            f"or export it in your shell before starting the app."
        )
    return value


def _as_bool(value):
    return str(value).strip().lower() in ("1", "true", "yes", "on")


OPENAI_API_KEY = _require("OPENAI_API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip() or DEV_SECRET_KEY
FLASK_DEBUG = _as_bool(os.environ.get("FLASK_DEBUG", "false"))
