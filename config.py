import os
import shutil
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
# OpenAI chat model used by every feature. OpenAI retires old models (e.g. gpt-4), so keep this configurable.
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "").strip() or "gpt-4o-mini"


def _find_tesseract():
    """ Locate the Tesseract OCR binary (needed by pytesseract), or exit with install instructions. """
    path = os.environ.get("TESSERACT_CMD", "").strip() or shutil.which("tesseract")
    if not path or not os.path.isfile(path):
        sys.exit(
            "❌ Tesseract OCR is not installed or not on your PATH. It is a system program, "
            "so `uv sync` does not install it.\n"
            "   macOS:          brew install tesseract\n"
            "   Ubuntu/Debian:  sudo apt install tesseract-ocr\n"
            "   Or set TESSERACT_CMD in .env to the full path of the tesseract executable."
        )
    return path


TESSERACT_CMD = _find_tesseract()
