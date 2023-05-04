from typing import Callable, Dict, Optional

from dx.plotting.utils import handle_view
from dx.types.charts.candlestick import DEXCandlestickChartView
from dx.types.charts.timeseries import DEXCumulativeLineChartView
from dx.types.charts.timeseries import DEXPercentLineChartView
from dx.types.charts.timeseries import DEXStackedAreaChartView
from dx.types.charts.timeseries import DEXPercentStackedAreaChartView

__all__ = [
    "candlestick",
    "cumulative",
    "line_percent",
    "stacked_area",
    "stacked_percent",
    "time_series_chart_functions",
]


def sample_candlestick(df, **kwargs) -> Optional[DEXCandlestickChartView]:
    return handle_view(df, chart_mode="candlestick", **kwargs)


def candlestick(df, **kwargs) -> Optional[DEXCandlestickChartView]:
    # TODO: define user-facing arguments and add documentation
    return sample_candlestick(df, **kwargs)


def sample_cumulative(df, **kwargs) -> Optional[DEXCumulativeLineChartView]:
    return handle_view(df, chart_mode="cumulative", **kwargs)


def cumulative(df, **kwargs) -> Optional[DEXCumulativeLineChartView]:
    # TODO: define user-facing arguments and add documentation
    return sample_cumulative(df, **kwargs)


def sample_line_percent(df, **kwargs) -> Optional[DEXPercentLineChartView]:
    return handle_view(df, chart_mode="line_percent", **kwargs)


def line_percent(df, **kwargs) -> Optional[DEXPercentLineChartView]:
    # TODO: define user-facing arguments and add documentation
    return sample_line_percent(df, **kwargs)


def sample_stacked_area(df, **kwargs) -> Optional[DEXStackedAreaChartView]:
    return handle_view(df, chart_mode="stacked_area", **kwargs)


def stacked_area(df, **kwargs) -> Optional[DEXStackedAreaChartView]:
    # TODO: define user-facing arguments and add documentation
    return sample_stacked_area(df, **kwargs)


def sample_stacked_percent(df, **kwargs) -> Optional[DEXPercentStackedAreaChartView]:
    return handle_view(df, chart_mode="stacked_percent", **kwargs)


def stacked_percent(df, **kwargs) -> Optional[DEXPercentStackedAreaChartView]:
    # TODO: define user-facing arguments and add documentation
    return sample_stacked_percent(df, **kwargs)


def time_series_chart_functions() -> Dict[str, Callable]:
    return {
        "candlestick": candlestick,
        "cumulative": cumulative,
        "line_percent": line_percent,
        "stacked_area": stacked_area,
        "stacked_percent": stacked_percent,
    }
