import logging
import uuid
from .context import correlation_id_var

class CorrelationIdFilter(logging.Filter):
    """
    A logging filter that adds a correlation ID to the log record.
    """
    def filter(self, record):
        correlation_id = correlation_id_var.get()
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
            correlation_id_var.set(correlation_id)
        record.correlation_id = correlation_id
        return True
