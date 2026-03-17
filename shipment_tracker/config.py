from pathlib import Path
import os

DEFAULT_DATA_DIR_NAME = "data"
DEFAULT_DATA_FILE_NAME = "shipments.json"
ENV_DATA_PATH = "SHIPMENT_TRACKER_DATA_PATH"

def get_default_data_path() -> Path:
    """Return the default path to the shipment data JSON file.

    If the SHIPMENT_TRACKER_DATA_PATH environment variable is set,
    that value is used. Otherwise, a "data/shipments.json" path
    is returned relative to the current working directory.
    """
    env_value = os.getenv(ENV_DATA_PATH)
    if env_value:
        return Path(env_value).expanduser().resolve()

    project_root = Path.cwd()
    return project_root / DEFAULT_DATA_DIR_NAME / DEFAULT_DATA_FILE_NAME
