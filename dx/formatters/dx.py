import uuid
from functools import lru_cache
from typing import Optional

import pandas as pd
import structlog
from IPython import get_ipython
from IPython.core.formatters import DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import HTML, display
from pandas.io.json import build_table_schema
from pydantic import BaseSettings, Field

from dx.filtering import SUBSET_FILTERS
from dx.formatters.main import DEFAULT_IPYTHON_DISPLAY_FORMATTER
from dx.sampling import get_df_dimensions, sample_if_too_big
from dx.settings import settings
from dx.utils.datatypes import to_dataframe
from dx.utils.formatting import is_default_index, normalize_index_and_columns
from dx.utils.tracking import (
    DISPLAY_ID_TO_ORIG_METADATA,
    SUBSET_TO_DATAFRAME_HASH,
    generate_df_hash,
    get_display_id,
    register_display_id,
    store_in_sqlite,
    track_column_conversions,
)


class DXSettings(BaseSettings):
    DX_DISPLAY_MAX_ROWS: int = 100_000
    DX_DISPLAY_MAX_COLUMNS: int = 50
    DX_HTML_TABLE_SCHEMA: bool = Field(True, allow_mutation=False)
    DX_MEDIA_TYPE: str = Field("application/vnd.dex.v1+json", allow_mutation=False)

    DX_FLATTEN_INDEX_VALUES: bool = False
    DX_FLATTEN_COLUMN_VALUES: bool = True
    DX_STRINGIFY_INDEX_VALUES: bool = False
    DX_STRINGIFY_COLUMN_VALUES: bool = True

    class Config:
        validate_assignment = True  # we need this to enforce `allow_mutation`
        json_encoders = {type: lambda t: str(t)}


@lru_cache
def get_dx_settings():
    return DXSettings()


dx_settings = get_dx_settings()

logger = structlog.get_logger(__name__)


def handle_dx_format(
    obj,
    ipython_shell: Optional[InteractiveShell] = None,
):
    ipython = ipython_shell or get_ipython()

    if not isinstance(obj, pd.DataFrame):
        obj = to_dataframe(obj)

    default_index_used = is_default_index(obj.index)

    if not settings.ENABLE_DATALINK:
        obj = normalize_index_and_columns(obj)
        payload, metadata = format_dx(
            obj,
            has_default_index=default_index_used,
        )
        return payload, metadata

    orig_obj = obj.copy()
    obj = normalize_index_and_columns(obj)
    obj_hash = generate_df_hash(obj)
    update_existing_display = obj_hash in SUBSET_TO_DATAFRAME_HASH
    applied_filters = SUBSET_FILTERS.get(obj_hash)
    display_id = get_display_id(obj_hash)
    if not update_existing_display:
        sqlite_df_table = register_display_id(
            obj,
            display_id=display_id,
            df_hash=obj_hash,
            ipython_shell=ipython,
        )

    track_column_conversions(
        orig_df=orig_obj,
        df=obj,
        display_id=display_id,
    )
    del orig_obj

    payload, metadata = format_dx(
        obj.copy(),
        update=update_existing_display,
        display_id=display_id,
        filters=applied_filters,
        has_default_index=default_index_used,
    )

    # this needs to happen after sending to the frontend
    # so the user doesn't wait as long for writing larger datasets
    if not update_existing_display:
        store_in_sqlite(sqlite_df_table, obj)

    return payload, metadata


class DXDisplayFormatter(DisplayFormatter):
    formatters = DEFAULT_IPYTHON_DISPLAY_FORMATTER.formatters

    def format(self, obj, **kwargs):

        if isinstance(obj, tuple(settings.RENDERABLE_OBJECTS)):
            handle_dx_format(obj)
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
    payload = {
        "schema": build_table_schema(df),
        "data": df.reset_index().transpose().values.tolist(),
        "datalink": {"display_id": display_id},
    }

    metadata = {
        "datalink": {
            "applied_filters": [],
            "dataframe_info": {},
            "display_id": display_id,
            "dx_settings": settings.dict(
                exclude={
                    "RENDERABLE_OBJECTS": True,
                    "DATETIME_STRING_FORMAT": True,
                    "MEDIA_TYPE": True,
                }
            ),
            "sample_history": [],
        },
        "display_id": display_id,
    }
    return (payload, metadata)


def format_dx(
    df: pd.DataFrame,
    update: bool = False,
    display_id: Optional[str] = None,
    filters: Optional[list] = None,
    has_default_index: bool = True,
) -> tuple:
    display_id = display_id or str(uuid.uuid4())

    # determine original dataset size, and truncated/sampled size if it's beyond the limits
    orig_df_dimensions = get_df_dimensions(df, prefix="orig")
    df = sample_if_too_big(df, display_id=display_id)
    sampled_df_dimensions = get_df_dimensions(df, prefix="truncated")

    payload, metadata = generate_dx_body(df, display_id=display_id)
    metadata["datalink"].update(
        {
            "dataframe_info": {
                "default_index_used": has_default_index,
                **orig_df_dimensions,
                **sampled_df_dimensions,
            },
            "applied_filters": filters or [],
            "sample_history": [],
            "sampling_time": pd.Timestamp("now").strftime(settings.DATETIME_STRING_FORMAT),
        }
    )

    if display_id not in DISPLAY_ID_TO_ORIG_METADATA:
        DISPLAY_ID_TO_ORIG_METADATA[display_id] = metadata

    payload = {dx_settings.DX_MEDIA_TYPE: payload}
    metadata = {dx_settings.DX_MEDIA_TYPE: metadata}

    # this needs to happen so we can update by display_id as needed
    with pd.option_context("html.table_schema", dx_settings.DX_HTML_TABLE_SCHEMA):
        display(
            payload,
            raw=True,
            metadata=metadata,
            display_id=display_id,
            update=update,
        )

    # temporary placeholder for copy/paste user messaging
    if settings.ENABLE_DATALINK:
        display(
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
    if get_ipython() is None and ipython_shell is None:
        return

    global settings
    settings.DISPLAY_MODE = "enhanced"

    settings_to_apply = {
        "DISPLAY_MAX_COLUMNS",
        "DISPLAY_MAX_ROWS",
        "MEDIA_TYPE",
        "FLATTEN_INDEX_VALUES",
        "FLATTEN_COLUMN_VALUES",
        "STRINGIFY_INDEX_VALUES",
        "STRINGIFY_COLUMN_VALUES",
    }
    for setting in settings_to_apply:
        val = getattr(dx_settings, f"DX_{setting}", None)
        setattr(settings, setting, val)

    ipython = ipython_shell or get_ipython()
    custom_formatter = DXDisplayFormatter()
    custom_formatter.formatters = DEFAULT_IPYTHON_DISPLAY_FORMATTER.formatters
    ipython.display_formatter = custom_formatter
