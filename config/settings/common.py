import logging
import os
from datetime import timedelta
from pathlib import Path
from corsheaders.defaults import default_headers

from config.docs import *  # noqa: F403
from config.logs import *  # noqa: F403

#################################
#       PROJECT ROOT DIR        #
#################################
BASE_DIR = Path(__file__).resolve().parent.parent.parent


##############################
#   DJANGO BASE SETTINGS     #
##############################
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = True if os.environ.get("DEBUG", "True") == "True" else False
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


##############################################
#     INTERNATIONALIZATION AND TIMEZONE      #
##############################################
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


##############################
#      INSTALLED APPS        #
##############################
INSTALLED_APPS = [
    # Default
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Internal Apps
    "db",
    "weather_api",
    "web_app",
    # Third Party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_structlog",
    # health checks
    "health_check",  # required
    # "health_check.db",  # stock Django health checkers
    "health_check.contrib.migrations",
]


#############################
#        MIDDLEWARES        #
#############################
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crum.CurrentRequestUserMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

#############################
#        TEMPLATES          #
#############################
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", os.path.join(BASE_DIR, "common", "util", "email_templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


#############################
#        DATABASES          #
#############################
# For postgre
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("POSTGRES_DB_NAME"),
#         "USER": os.environ.get("POSTGRES_DB_USER"),
#         "PASSWORD": os.environ.get("POSTGRES_DB_PASSWORD"),
#         "HOST": os.environ.get("POSTGRES_DB_HOST"),
#         "PORT": os.environ.get("POSTGRES_DB_PORT"),
#         "OPTIONS": (
#             {}
#             if os.environ.get("POSTGRES_DB_SSL_ENABLED", "False") == "False"
#             else {"sslmode": "verify-full", "sslrootcert": "./postgresql_ssl_cert.pem"}
#         ),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 4294967296  # 4GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 4294967296  # 4GB

#############################
#       STATIC FILES        #
#############################
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


########################################
#       REST FRAMEWORK SETTINGS        #
########################################
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.FileUploadParser",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
}


#################################
#       JWT AUTH SETTINGS       #
#################################
SIMPLE_JWT = {
    "BLACKLIST_DB_ALIAS": "default",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=float(os.getenv("ACCESS_TOKEN_LIFETIME_IN_MINUTES", 15))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=float(os.getenv("REFRESH_TOKEN_LIFETIME_IN_DAYS", 7))),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


#############################
#       CORS SETTINGS       #
#############################
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    *default_headers,
    "x-request-id",
]
CORS_EXPOSE_HEADERS = [
    "x-request-id",
]


###############################
#     DOCKER IMAGE INFO       #
###############################
DOCKER_IMAGE_REPO = os.environ.get("DOCKER_IMAGE_REPO")
DOCKER_IMAGE_TAG = os.environ.get("DOCKER_IMAGE_TAG")


#############################
#     STRUCTLOG SETTINGS    #
#############################
DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL = logging.INFO
DJANGO_STRUCTLOG_USER_ID_FIELD = "id"

#############################
#     MetOffice Base URL    #
#############################
METOFFICE_BASE_URL = 'https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/'
