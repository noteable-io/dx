from functools import lru_cache
from typing import Optional

from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell
from pydantic import Field

from dx.formatters.main import DEFAULT_IPYTHON_DISPLAY_FORMATTER, DXDisplayFormatter
from dx.settings import get_settings
from pydantic_settings import BaseSettings, SettingsConfigDict

settings = get_settings()


class DataResourceSettings(BaseSettings):
    # "simple" (classic simpleTable/DEX) display mode
    DATARESOURCE_DISPLAY_MAX_ROWS: int = 50_000
    DATARESOURCE_DISPLAY_MAX_COLUMNS: int = 50
    DATARESOURCE_MAX_STRING_LENGTH: int = 250
    DATARESOURCE_HTML_TABLE_SCHEMA: bool = Field(True, frozen=True)
    DATARESOURCE_MEDIA_TYPE: str = Field("application/vnd.dataresource+json", frozen=True)

    DATARESOURCE_FLATTEN_INDEX_VALUES: bool = False
    DATARESOURCE_FLATTEN_COLUMN_VALUES: bool = True
    DATARESOURCE_STRINGIFY_INDEX_VALUES: bool = False
    DATARESOURCE_STRINGIFY_COLUMN_VALUES: bool = True
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = SettingsConfigDict(validate_assignment=True, json_encoders={type: lambda t: str(t)})


@lru_cache
def get_dataresource_settings():
    return DataResourceSettings()


dataresource_settings = get_dataresource_settings()


def deregister(ipython_shell: Optional[InteractiveShell] = None) -> None:
    """
    Sets the current IPython display formatter as the dataresource
    display formatter, used for simpleTable / "classic DEX" outputs
    and updates global dx & pandas settings with dataresource settings.
    """
    if get_ipython() is None and ipython_shell is None:
        return

    global settings
    settings.DISPLAY_MODE = "simple"

    settings_to_apply = {
        "DISPLAY_MAX_COLUMNS",
        "DISPLAY_MAX_ROWS",
        "MAX_STRING_LENGTH",
        "MEDIA_TYPE",
        "FLATTEN_INDEX_VALUES",
        "FLATTEN_COLUMN_VALUES",
        "STRINGIFY_INDEX_VALUES",
        "STRINGIFY_COLUMN_VALUES",
    }
    for setting in settings_to_apply:
        val = getattr(dataresource_settings, f"DATARESOURCE_{setting}", None)
        setattr(settings, setting, val)

    ipython = ipython_shell or get_ipython()

    custom_formatter = DXDisplayFormatter()
    custom_formatter.formatters = DEFAULT_IPYTHON_DISPLAY_FORMATTER.formatters
    ipython.display_formatter = custom_formatter
