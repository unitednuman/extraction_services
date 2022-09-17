import os

from .base import *

if os.getenv("django_sqlite"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": "5432",
        }
    }

# Log everything to the logs directory at the top
LOGFILE_ROOT = BASE_DIR.parent / "logs"


EMAIL_FILE_PATH = str(LOGFILE_ROOT / "emails")
