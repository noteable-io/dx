import warnings
from functools import lru_cache
from typing import Optional

import pandas as pd
from IPython import get_ipython
from IPython.core.formatters import DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from pydantic import BaseSettings, Field

from dx.config import DEFAULT_IPYTHON_DISPLAY_FORMATTER, IN_IPYTHON_ENV
from dx.settings import get_settings

settings = get_settings()
warnings.filterwarnings("ignore")


DISPLAY_ID_TO_DATAFRAME = {}


class PandasSettings(BaseSettings):
    # "plain" (pandas) display mode
    PANDAS_DISPLAY_MAX_ROWS: int = 60
    PANDAS_DISPLAY_MAX_COLUMNS: int = 20
    PANDAS_HTML_TABLE_SCHEMA: bool = Field(False, allow_mutation=False)
    PANDAS_MEDIA_TYPE: str = Field("application/vnd.dataresource+json", allow_mutation=False)

    class Config:
        validate_assignment = True  # we need this to enforce `allow_mutation`


@lru_cache
def get_pandas_settings():
    return PandasSettings()


pandas_settings = get_pandas_settings()


def reset(ipython_shell: Optional[InteractiveShell] = None) -> None:
    """
    Resets all nteract/Noteable options, reverting to the default
    pandas display options and IPython display formatter.
    """
    if not IN_IPYTHON_ENV and ipython_shell is None:
        return

    global settings
    settings.DISPLAY_MODE = "plain"

    settings.DISPLAY_MAX_COLUMNS = pandas_settings.PANDAS_DISPLAY_MAX_COLUMNS
    settings.DISPLAY_MAX_ROWS = pandas_settings.PANDAS_DISPLAY_MAX_ROWS
    settings.MEDIA_TYPE = pandas_settings.PANDAS_MEDIA_TYPE

    pd.set_option("display.max_columns", pandas_settings.PANDAS_DISPLAY_MAX_COLUMNS)
    pd.set_option("display.max_rows", pandas_settings.PANDAS_DISPLAY_MAX_ROWS)

    ipython = ipython_shell or get_ipython()
    ipython.display_formatter = DEFAULT_IPYTHON_DISPLAY_FORMATTER or DisplayFormatter()
