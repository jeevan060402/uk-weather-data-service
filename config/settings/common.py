import logging
import os
from datetime import timedelta
from pathlib import Path

from azure.identity import DefaultAzureCredential
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
ENABLE_TRACING = True if os.environ.get("ENABLE_TRACING", "True") == "True" else False
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
    # Third Party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "storages",
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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB_NAME"),
        "USER": os.environ.get("POSTGRES_DB_USER"),
        "PASSWORD": os.environ.get("POSTGRES_DB_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_DB_HOST"),
        "PORT": os.environ.get("POSTGRES_DB_PORT"),
        "OPTIONS": (
            {}
            if os.environ.get("POSTGRES_DB_SSL_ENABLED", "False") == "False"
            else {"sslmode": "verify-full", "sslrootcert": "./postgresql_ssl_cert.pem"}
        ),
    }
}

#############################
#       AZURE CREDS         #
#############################
USE_MANAGED_IDENTITY = True if os.environ.get("USE_MANAGED_IDENTITY", "False") == "True" else False
# Azure Blob storage account
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_NAME_SFTP = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME_SFTP")
# Azure Blob storage container
AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER")
AZURE_PUBLIC_CONTAINER = os.environ.get("AZURE_PUBLIC_CONTAINER")
# authentication settings should be removed in future
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
AZURE_STORAGE_ACCOUNT_KEY_SFTP = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY_SFTP")
# Optional
AZURE_URL_EXPIRATION_SECS = 3600


########################################
#       AZURE SERVICEBUS CREDS         #
########################################
AZURE_SERVICE_BUS_NAMESPACE = os.environ.get("AZURE_SERVICE_BUS_NAMESPACE")
AZURE_SERVICE_BUS_QUEUE = os.environ.get("AZURE_SERVICE_BUS_QUEUE")


#############################
#       STORAGE ENGINE      #
#############################
STORAGES = {
    "default": {
        "BACKEND": "config.storages.CustomAzureStorage",
        "OPTIONS": {
            "account_name": AZURE_ACCOUNT_NAME,
            "azure_container": AZURE_CONTAINER,
            "account_key": AZURE_ACCOUNT_KEY if not USE_MANAGED_IDENTITY else None,
            "token_credential": DefaultAzureCredential() if USE_MANAGED_IDENTITY else None,
        },
    },
    "staticfiles": {  # Static files
        "BACKEND": "config.storages.CustomAzureStorage",
        "OPTIONS": {
            "account_name": AZURE_ACCOUNT_NAME,
            "azure_container": AZURE_PUBLIC_CONTAINER,
            "account_key": AZURE_ACCOUNT_KEY if not USE_MANAGED_IDENTITY else None,
            "token_credential": DefaultAzureCredential() if USE_MANAGED_IDENTITY else None,
            "expiration_secs": None,
            "location": "static",  # Folder prefix for static files
        },
    },
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 4294967296  # 4GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 4294967296  # 4GB


#############################
#       STATIC FILES        #
#############################
STATIC_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER}/static/"


#############################
#       MEDIA FILES         #
#############################
MEDIA_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER}/"


##############################
#      EMAIL SETTINGS        #
##############################
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# server settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
# Authentication settings
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
# Default sender settings
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_HOST_USER")
EMAIL_INTERCEPTOR = os.environ.get("EMAIL_INTERCEPTOR")


########################################
#       REST FRAMEWORK SETTINGS        #
########################################
REST_FRAMEWORK = {
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


################################
# EMAIL SERVICE CONFIGURATION  #
################################
ENABLE_EMAIL = True if os.environ.get("ENABLE_EMAIL", "False") == "True" else False
FRONTEND_LOGIN_URL = os.environ.get("FRONTEND_LOGIN_URL")
AZURE_EMAIL_URL = os.environ.get("AZURE_EMAIL_URL")
AZURE_EMAIL_KEY = os.environ.get("AZURE_EMAIL_KEY")
AZURE_EMAIL_HOST = os.environ.get("AZURE_EMAIL_HOST")
EMAIL_INTERCEPTOR = os.environ.get("EMAIL_INTERCEPTOR")


##############################################
#         SYSTEM ADMIN INSTANCE INFO         #
##############################################
SYSTEM_ADMIN_BASE_URL = os.environ.get("SYSTEM_ADMIN_BASE_URL")
SYSTEM_ADMIN_TOKEN = os.environ.get("SYSTEM_ADMIN_TOKEN")
SYSTEM_ADMIN_CLIENT_ID = os.environ.get("SYSTEM_ADMIN_CLIENT_ID")


##############################
#     L4 INSTANCE INFO       #
##############################
ALTIUSHUB_INTEGRATION_BASE_URL = os.environ.get("ALTIUSHUB_INTEGRATION_BASE_URL")
ALTIUSHUB_INTEGRATION_KEY = os.environ.get("ALTIUSHUB_INTEGRATION_KEY")


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
