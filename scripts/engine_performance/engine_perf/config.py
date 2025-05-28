import json
import os
import sys

from .logger import logger


def load_configuration(config_filename="config.json"):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(parent_dir, config_filename)
    try:
        with open(config_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logger.error(f"Configuration file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Error decoding '{config_path}'. Please check the file format.")
        sys.exit(1)
