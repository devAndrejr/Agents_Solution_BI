import logging.config
import os
from core.config.config import Config # Import Config

# Check if python-json-logger is installed
try:
    import pythonjsonlogger.jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False

# Check if sentry-sdk is installed
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

def setup_logging():
    """
    Configures the logging for the application using a dictionary configuration.
    """
    LOGS_DIR = "logs"
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        print(f"Diretório de logs criado em: {os.path.abspath(LOGS_DIR)}") # Debug print

    # Base formatter
    formatter = "json" if JSON_LOGGER_AVAILABLE else "simple"

    # Get the desired log level from Config
    app_log_level = "DEBUG" # <--- TEMPORARY CHANGE FOR DEBUGGING

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "core.utils.correlation_id.CorrelationIdFilter",
            },
        },
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(lineno)d %(pathname)s %(correlation_id)s",
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": app_log_level, # Use the configured log level
                "formatter": "simple",
                "stream": "ext://sys.stdout",
                "filters": ["correlation_id"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO", # File handler can remain INFO or higher
                "formatter": formatter,
                "filename": os.path.join(LOGS_DIR, "app.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
                "filters": ["correlation_id"],
            },
            "audit_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": formatter,
                "filename": os.path.join(LOGS_DIR, "audit.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
                "filters": ["correlation_id"],
            },
        },
        "loggers": {
            "": { # Root logger
                "level": app_log_level, # Use the configured log level
                "handlers": ["console", "file"],
            },
            "streamlit": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "core": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "audit": {
                "level": "INFO",
                "handlers": ["audit_file"],
                "propagate": False,
            },
        },
    }

    # If json logger is not available, we need to remove it from the config
    if not JSON_LOGGER_AVAILABLE:
        del logging_config["formatters"]["json"]

    if SENTRY_AVAILABLE and os.getenv("SENTRY_DSN"):
        logging_config["handlers"]["sentry"] = {
            "class": "sentry_sdk.integrations.logging.EventHandler",
            "level": "ERROR",
        }
        logging_config["loggers"][""]["handlers"].append("sentry")

    logging.config.dictConfig(logging_config)