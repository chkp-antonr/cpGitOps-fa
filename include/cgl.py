""" Constants and Globals """

import os
from typing import Union
from pydantic_settings import BaseSettings

#region Settings
# https://progressstory.com/tech/configuration-management-python-pydantic/
class Base(BaseSettings):
    DIR_SSOT: str = "../SSoT"
    DIR_GW: str = "Gateways"
    DIR_MGMT: str = "Management"

    FN_DESCR: str = "_descr_.yaml"

    MGMT_DIR_DECL: str = "DECLARED" # YAML
    MGMT_DIR_TEMP: str = "TEMPCURR" # JSON (Current from API - temporary storage)
    MGMT_DIR_LAST: str = "LASTSAVED" # JSON (Last saved good config )


    GW_GLOBAL: str = "Global"
    GW_CLISH: str = "clish.txt"
    GW_EXCLUDE: str = "exclusions.yaml"
    GW_TEMPLATES: str = "templates.yaml"

    # SECRET_KEY: str = Field('random_string', env='ANOTHER_SECRET_KEY')
    class Config:
        case_sensitive = False
        env_file = '.env' # This is the key factor

class Prod(Base):
    # username = "Production"
    # port = 5051

    class Config:
        env_file = 'prod.env'

class Dev(Base):
    # username = "TRIPATHI"

    class Config:
        case_sensitive = False
        env_file = 'dev.env'

class Test(Base):
    DIR_SSOT: str = "../SSoT-test"

    class Config:
        case_sensitive = False
        env_file = 'dev.env'


config = dict(
    dev=Dev,
    prod=Prod,
    test=Test,
)
settings: Union[Dev, Prod, Test] = config[os.environ.get('ENV', 'dev').lower()]()
#endregion Settings

#region Logging
# LOGFORMAT_COLOR = "  %(color_message)s%(levelname)-8s | %(message)s"
LOGFORMAT_COLOR = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
LOGFORMAT_COLOR_DEBUG = "  %(log_color)s%(levelname)-8s%(reset)s | %(module)s.%(funcName)s@%(lineno)d | %(log_color)s%(message)s%(reset)s"

LOGFORMAT = "  %(levelname)-8s | %(message)s"
LOGFORMAT_DEBUG = "  %(levelname)-8s | %(module)s.%(funcName)s@%(lineno)d | %(message)s"

import logging

from uvicorn.logging import ColourizedFormatter
class ColorFormatter(ColourizedFormatter):
    log_colors = {
      logging.DEBUG:    'bright_black',
      logging.INFO:     'green',
      logging.WARNING:  'yellow',
      logging.ERROR:    'red',
      logging.CRITICAL: 'bright_red', # 'red,bg_white',
    }
    def format(self, record):
        import click
        if record.levelno == logging.DEBUG:
            self._style._fmt = click.style(f"{LOGFORMAT_DEBUG}", fg=self.log_colors[record.levelno])
        else:
            # self._style._fmt = cgl.LOGFORMAT + click.style(" []", fg="cyan")
            self._style._fmt = click.style(f"{LOGFORMAT}", fg=self.log_colors[record.levelno])
        return super().format(record)

# Use it for colored logging
logger = logging.getLogger("custom")
def prepare_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter(use_colors=True))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

#endregion Logging
