from .base import *
import logging.config


DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': "db.sqlite3",
     }
 }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': env('POSTGRES_DB'),
#         'USER': env('POSTGRES_USER'),
#         'PASSWORD': env('POSTGRES_PASSWORD'),
#         'HOST': env('POSTGRES_HOST'),
#         'PORT': '5432',
#     }
# }

# Log everything to the logs directory at the top
LOGFILE_ROOT = BASE_DIR.parent / "logs"

# Reset logging
# (see http://www.caktusgroup.com/blog/2015/01/27/Django-Logging-Configuration-logging_config-default-settings-logger/)

# LOGGING_CONFIG = None
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
#             "datefmt": "%d/%b/%Y %H:%M:%S",
#         },
#         "simple": {"format": "%(levelname)s %(message)s"},
#     },
#     "handlers": {
#         "django_log_file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": str(LOGFILE_ROOT / "django.log"),
#             "formatter": "verbose",
#         },
#         "proj_log_file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": str(LOGFILE_ROOT / "project.log"),
#             "formatter": "verbose",
#         },
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#             "formatter": "simple",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["django_log_file"],
#             "propagate": True,
#             "level": "DEBUG",
#         },
#         "project": {"handlers": ["proj_log_file"], "level": "DEBUG"},
#     },
# }

# logging.config.dictConfig(LOGGING)

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = str(LOGFILE_ROOT / "emails")


DEFAULT_FROM_EMAIL = 'no-reply@tyudirectory.org'
SERVER_EMAIL = 'webmaster@tyudirectory.org'


