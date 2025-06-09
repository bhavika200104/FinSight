import json
import os

# File to persist portfolio data
DATA_PATH = "data/portfolio.json"

def load_investments():
    """Load the portfolio data from disk."""
    if not os.path.exists(DATA_PATH):
        return {}
    try:
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_investments(data):
    """Save the portfolio data to disk."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)
