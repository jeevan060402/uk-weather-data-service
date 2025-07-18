"""
WSGI config for altius project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()

try:
    ENABLE_TRACING = os.environ.get("ENABLE_TRACING")
    if ENABLE_TRACING == "True":
        pass
except:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()
