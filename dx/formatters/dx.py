import uuid
from functools import lru_cache
from typing import Optional, Set

import numpy as np
import pandas as pd
import structlog
from IPython import get_ipython
from IPython.core.formatters import DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import HTML
from IPython.display import display as ipydisplay
from pandas.io.json import build_table_schema
from pydantic import BaseSettings, Field

from dx.config import DEFAULT_IPYTHON_DISPLAY_FORMATTER, IN_IPYTHON_ENV
from dx.filtering import get_applied_filters
from dx.sampling import sample_and_describe
from dx.settings import settings
from dx.utils.datatypes import to_dataframe
from dx.utils.formatting import is_default_index, normalize_index_and_columns
from dx.utils.tracking import df_is_subset, get_display_id, register_display_id, store_in_sqlite


class DXSettings(BaseSettings):
    DX_DISPLAY_MAX_ROWS: int = 100_000
    DX_DISPLAY_MAX_COLUMNS: int = 50
    DX_HTML_TABLE_SCHEMA: bool = Field(True, allow_mutation=False)
    DX_MEDIA_TYPE: str = Field("application/vnd.dex.v1+json", allow_mutation=False)
    DX_RENDERABLE_OBJECTS: Set[type] = {pd.Series, pd.DataFrame, np.ndarray}

    DX_FLATTEN_INDEX_VALUES: bool = False
    DX_FLATTEN_COLUMN_VALUES: bool = True
    DX_STRINGIFY_INDEX_VALUES: bool = True
    DX_STRINGIFY_COLUMN_VALUES: bool = True

    class Config:
        validate_assignment = True  # we need this to enforce `allow_mutation`
        json_encoders = {type: lambda t: str(t)}


@lru_cache
def get_dx_settings():
    return DXSettings()


dx_settings = get_dx_settings()

logger = structlog.get_logger(__name__)


class DXDisplayFormatter(DisplayFormatter):
    def format(self, obj, **kwargs):

        if isinstance(obj, tuple(settings.RENDERABLE_OBJECTS)):
            if not isinstance(obj, pd.DataFrame):
                obj = to_dataframe(obj)
            update_existing_display = df_is_subset(obj)
            applied_filters = get_applied_filters(obj)
            display_id = get_display_id(obj)
            df_uuid = register_display_id(
                obj,
                display_id=display_id,
                is_subset=update_existing_display,
            )

            format_dx(
                obj.copy(),
                update=update_existing_display,
                display_id=display_id,
                filters=applied_filters,
            )

            # this needs to happen after sending to the frontend
            # so the user doesn't wait as long for writing larger datasets
            store_in_sqlite(df_uuid, obj)

            return ({}, {})

        return DEFAULT_IPYTHON_DISPLAY_FORMATTER.format(obj, **kwargs)


def generate_dx_body(
    df: pd.DataFrame,
    display_id: Optional[str] = None,
) -> tuple:
    """
    Transforms the dataframe to a payload dictionary containing the
    table schema and column values as arrays.
    """
    # this will include the `df.index` by default (e.g. slicing/sampling)
    payload_body = {
        "schema": build_table_schema(df),
        "data": df.reset_index().transpose().values.tolist(),
        "datalink": {},
    }
    payload = {dx_settings.DX_MEDIA_TYPE: payload_body}

    metadata_body = {
        "datalink": {
            "dataframe_info": {},
            "dx_settings": settings.json(exclude={"RENDERABLE_OBJECTS": True}),
            "applied_filters": [],
        },
    }
    metadata = {dx_settings.DX_MEDIA_TYPE: metadata_body}

    display_id = display_id or str(uuid.uuid4())
    payload_body["datalink"]["display_id"] = display_id
    metadata_body["datalink"]["display_id"] = display_id

    return (payload, metadata)


def format_dx(
    df: pd.DataFrame,
    update: bool = False,
    display_id: Optional[str] = None,
    filters: Optional[list] = None,
) -> tuple:
    default_index_used = is_default_index(df.index)
    df = normalize_index_and_columns(df)
    df, dataframe_info = sample_and_describe(df, display_id=display_id)
    dataframe_info["default_index_used"] = default_index_used
    payload, metadata = generate_dx_body(df, display_id=display_id)
    metadata[dx_settings.DX_MEDIA_TYPE]["datalink"].update(
        {
            "dataframe_info": dataframe_info,
            "applied_filters": filters,
        }
    )

    # don't pass a dataframe in here, otherwise you'll get recursion errors
    with pd.option_context("html.table_schema", dx_settings.DX_HTML_TABLE_SCHEMA):
        ipydisplay(
            payload,
            raw=True,
            metadata=metadata,
            display_id=display_id,
            update=update,
        )

    # temporary placeholder for copy/paste user messaging
    ipydisplay(
        HTML("<div></div>"),
        display_id=display_id + "-primary",
        update=update,
    )

    return (payload, metadata)


def register(ipython_shell: Optional[InteractiveShell] = None) -> None:
    """
    Enables the DEX media type output display formatting and
    updates global dx & pandas settings with DX settings.
    """
    if not IN_IPYTHON_ENV and ipython_shell is None:
        return

    global settings
    settings.DISPLAY_MODE = "enhanced"

    settings_to_apply = {
        "DISPLAY_MAX_COLUMNS",
        "DISPLAY_MAX_ROWS",
        "MEDIA_TYPE",
        "RENDERABLE_OBJECTS",
        "FLATTEN_INDEX_VALUES",
        "FLATTEN_COLUMN_VALUES",
        "STRINGIFY_INDEX_VALUES",
        "STRINGIFY_COLUMN_VALUES",
    }
    for setting in settings_to_apply:
        val = getattr(dx_settings, f"DX_{setting}", None)
        setattr(settings, setting, val)

    ipython = ipython_shell or get_ipython()
    ipython.display_formatter = DXDisplayFormatter()
