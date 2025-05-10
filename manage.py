#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv

from config.tracing import load_traces

load_dotenv()


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

    print("############################ DATABASES ############################")
    print(f"PostgreSQL: {os.environ.get('POSTGRES_DB_NAME')}")
    print("###################################################################")

    try:
        ENABLE_TRACING = os.environ.get("ENABLE_TRACING")
        if ENABLE_TRACING == "True":
            load_traces()
    except:
        pass

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
