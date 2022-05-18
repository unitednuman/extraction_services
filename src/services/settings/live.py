from .base import *


MIDDLEWARE.extend([
    'whitenoise.middleware.WhiteNoiseMiddleware'
])

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Log everything to the logs directory at the top
LOGFILE_ROOT = BASE_DIR.parent / "logs"

# # Reset logging
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
#     "loggers": {"project": {"handlers": ["proj_log_file"], "level": "DEBUG"}},
# }

# logging.config.dictConfig(LOGGING)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': '5432',
    }
}


'''EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_REGION_NAME = env('AWS_REGION_NAME')
AWS_DEFAULT_REGION = AWS_REGION_NAME

DEFAULT_FROM_EMAIL = 'no-reply@tyudirectory.org'
SERVER_EMAIL = 'webmaster@tyudirectory.org'

ANYMAIL = {
    'AMAZON_SES_CLIENT_PARAMS': {
        'aws_access_key_id': AWS_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
        'region_name': AWS_DEFAULT_REGION
    }
}
'''
