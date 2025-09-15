import pandas as pd
import numpy as np
from decimal import Decimal
import datetime

def _clean_json_values(obj):
    """
    Recursively cleans NaN, NaT, Decimal, and Timestamp values from a dictionary or list,
    replacing them with JSON-serializable equivalents to ensure JSON compliance.
    """
    if isinstance(obj, dict):
        return {k: _clean_json_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_json_values(elem) for elem in obj]
    elif pd.isna(obj): # Handles both np.nan and pd.NaT
        return None
    elif isinstance(obj, Decimal):
        # Convert Decimal to float for JSON serialization
        return float(obj)
    elif isinstance(obj, (np.integer, np.floating)):
        # Convert numpy types to Python native types
        return obj.item()
    elif isinstance(obj, (pd.Timestamp, datetime.datetime)):
        # Convert Timestamp to ISO string for JSON serialization
        return obj.isoformat() if not pd.isna(obj) else None
    elif isinstance(obj, datetime.date):
        # Convert date to ISO string
        return obj.isoformat()
    else:
        return obj
