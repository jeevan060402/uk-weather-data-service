import logging
import os
from contextlib import contextmanager
from pathlib import Path

import pytz
import structlog
from django.dispatch import receiver
from django.utils.timezone import datetime
from django_structlog import signals

#####################################
#         LOGGING SETTINGS          #
#####################################
BASE_DIR = Path(__file__).resolve().parent.parent
LOGGING_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)

# Setup logging
DEFAULT_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "DEBUG")


def add_extra_context_to_logs(
    logger: logging.Logger, method_name: str, event_dict: structlog.types.EventDict
) -> structlog.types.EventDict:
    # Add ist time
    event_dict["ist_time"] = datetime.now().astimezone(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    # Add PID and TID
    event_dict["pid"] = os.getpid()

    return event_dict


# To enable standard library logs to be formatted via structlog, we add this
# `foreign_pre_chain` to both formatters.
foreign_pre_chain = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    add_extra_context_to_logs,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        *foreign_pre_chain,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


# Configure all logs to be handled by structlog `ProcessorFormatter` and
# rendered either as pretty colored console lines or as single JSON lines.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": foreign_pre_chain,
        },
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": foreign_pre_chain,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "null": {
            "class": "logging.NullHandler",
        },
        "file_write": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "django.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 100,
            "formatter": "json",
        },
        # UNUSED
        "store_in_memory": {
            "level": "DEBUG",
            "class": "logging.handlers.MemoryHandler",
            "target": "flush_to_disk",
            "formatter": "json",
            "capacity": 1,
            "flushLevel": logging.ERROR,
            "flushOnClose": True,
        },
        "flush_to_disk": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "django.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 100,
            "formatter": "json",
        },
    },
    "loggers": {
        "default": {"handlers": ["file_write", "console"], "level": DEFAULT_LOG_LEVEL, "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["file_write", "console"], "level": "WARNING", "propagate": False},
        "django_structlog.middlewares.request": {"handlers": ["null"], "level": "ERROR", "propagate": False},
    },
}


######################################
#       LOGGING CONTEXT MANAGER      #
######################################
@contextmanager
def log_context_manager(**kwargs):
    """
    Context manager to apply logging context using structlog.
    """
    structlog.contextvars.bind_contextvars(**kwargs)
    try:
        yield
    finally:
        structlog.contextvars.clear_contextvars()


#################################################################  SIGNALS ############################################################


@receiver(signals.bind_extra_request_metadata)
def bind_request_metadata(request, logger, log_kwargs, **kwargs):
    try:
        from rest_framework_simplejwt.tokens import AccessToken

        header = request.META.get("HTTP_AUTHORIZATION")
        user_id = None
        if header:
            raw_token = header.split()[1]
            token = AccessToken(raw_token)
            user_id = token["user_id"]
        # Bind context variables
        structlog.contextvars.bind_contextvars(
            request_path=request.path,
            request_method=request.method,
            request_query_params=dict(request.GET),
            user_id=user_id,
            remote_addr=request.META.get("REMOTE_ADDR"),
        )
    except Exception:
        pass


@receiver(signals.bind_extra_request_finished_metadata)
def bind_extra_request_finished_metadata(request, response, logger, log_kwargs, **kwargs):
    # Bind context variables
    structlog.contextvars.bind_contextvars(
        request_path=request.path,
        request_method=request.method,
        request_query_params=dict(request.GET),
        remote_addr=request.META.get("REMOTE_ADDR"),
        response_status_code=response.status_code,
    )


@receiver(signals.bind_extra_request_failed_metadata)
def bind_extra_request_failed_metadata(request, logger, exception, log_kwargs, **kwargs):
    # Bind context variables
    structlog.contextvars.bind_contextvars(
        request_path=request.path,
        request_method=request.method,
        request_query_params=dict(request.GET),
        remote_addr=request.META.get("REMOTE_ADDR"),
    )


@receiver(signals.update_failure_response)
def update_failure_response(request, response, logger, exception, **kwargs):
    context = structlog.contextvars.get_merged_contextvars(logger)
    response["X-Request-ID"] = context["request_id"]
    # Bind context variables
    structlog.contextvars.bind_contextvars(
        request_path=request.path,
        request_method=request.method,
        request_query_params=dict(request.GET),
        remote_addr=request.META.get("REMOTE_ADDR"),
        response_status_code=response.status_code,
    )
