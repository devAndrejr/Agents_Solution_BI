import logging
import logging.config
import os
from datetime import datetime

def setup_logging():
    """
    Configures file-based and stream-based logging for the application.
    """
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Define subdirectories for different logs
    activity_log_dir = os.path.join(logs_dir, "app_activity")
    error_log_dir = os.path.join(logs_dir, "errors")
    interaction_log_dir = os.path.join(logs_dir, "user_interactions")
    os.makedirs(activity_log_dir, exist_ok=True)
    os.makedirs(error_log_dir, exist_ok=True)
    os.makedirs(interaction_log_dir, exist_ok=True)

    # Generate date-stamped filenames
    current_date = datetime.now().strftime("%Y-%m-%d")
    activity_log_file = os.path.join(activity_log_dir, f"activity_{current_date}.log")
    error_log_file = os.path.join(error_log_dir, f"error_{current_date}.log")
    interaction_log_file = os.path.join(interaction_log_dir, f"interactions_{current_date}.log")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "interaction": {
                "format": "%(asctime)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            },
            "activity_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": activity_log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "INFO",
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": error_log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "ERROR",
                "encoding": "utf-8",
            },
            "interaction_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "interaction",
                "filename": interaction_log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "INFO",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "user_interaction": {
                "handlers": ["interaction_file"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console", "activity_file", "error_file"],
            "level": "INFO",
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging configured successfully.")