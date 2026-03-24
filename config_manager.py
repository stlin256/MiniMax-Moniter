import base64
import os
import json

CONFIG_FILE = "config.b64"

def save_config(api_key: str, opacity: int = 230, model: str = "MiniMax-M*", geometry: dict = None):
    """
    Saves the config to a base64 encoded JSON file.
    """
    data = {
        "api_key": api_key,
        "opacity": opacity,
        "model": model,
        "geometry": geometry
    }
    encoded = base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
    with open(CONFIG_FILE, "w", encoding='utf-8') as f:
        f.write(encoded)

def load_config() -> dict:
    """
    Loads the config from a base64 encoded JSON file.
    """
    default = {"api_key": "", "opacity": 230, "model": "MiniMax-M*", "geometry": None}
    if not os.path.exists(CONFIG_FILE):
        return default
    try:
        with open(CONFIG_FILE, "r", encoding='utf-8') as f:
            encoded = f.read().strip()
            if not encoded:
                return default
            data = json.loads(base64.b64decode(encoded).decode('utf-8'))
            return {**default, **data}
    except Exception:
        return default

# Keep old functions for compatibility or refactor app.py to use load_config
def load_api_key() -> str:
    return load_config()["api_key"]

def save_api_key(api_key: str):
    config = load_config()
    save_config(api_key, config["opacity"], config["model"])

def has_api_key() -> bool:
    return len(load_api_key()) > 0
