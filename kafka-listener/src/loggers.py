import logging
import logging.config
from os.path import exists, join
import sys

import yaml

from src.config import settings


__all__ = ("set_logging",)


def set_logging() -> None:
    """
    Setting up logging module
    """

    files = [".logging.dev.yaml", ".logging.yaml"]
    for file in files:
        ls_file = join(settings.base_dir, file)
        if exists(ls_file):
            with open(ls_file) as f:
                config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
            break
    else:
        print(f'No logging config found: {", ".join(files)}')
        sys.exit(0)
