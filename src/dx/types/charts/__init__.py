from typing import Union

from pydantic import Field
from typing_extensions import Annotated

from dx.types.charts.adjacency_matrix import DEXAdjacencyMatrixChartView
from dx.types.charts.arc_diagram import DEXArcDiagramChartView
from dx.types.charts.bar import DEXBarChartView
from dx.types.charts.bignumber import DEXBigNumberChartView
from dx.types.charts.candlestick import DEXCandlestickChartView
from dx.types.charts.choropleth import DEXChoroplethChartView
from dx.types.charts.correlation_matrix import DEXCorrelationMatrixChartView
from dx.types.charts.cumulative import DEXCumulativeChartView
from dx.types.charts.dataprism import DEXDataPrismChartView
from dx.types.charts.dendrogram import DEXDendrogramChartView
from dx.types.charts.dimension_matrix import DEXDimensionMatrixChartView
from dx.types.charts.diverging_bar import DEXDivergingBarChartView
from dx.types.charts.donut import DEXDonutChartView
from dx.types.charts.dotplot import DEXDotPlotChartView
from dx.types.charts.flow_diagram import DEXFlowDiagramChartView
from dx.types.charts.force_directed_network import DEXForceDirectedNetworkChartView
from dx.types.charts.funnel import DEXFunnelChartView
from dx.types.charts.funnel_chart import DEXFunnelChartChartView
from dx.types.charts.funnel_sunburst import DEXFunnelSunburstChartView
from dx.types.charts.funnel_tree import DEXFunnelTreeChartView
from dx.types.charts.hexbin import DEXHexbinChartView
from dx.types.charts.line import DEXLineChartView
from dx.types.charts.line_percent import DEXLinePercentChartView
from dx.types.charts.parcoords import DEXParallelCoordinatesChartView
from dx.types.charts.partition import DEXPartitionChartView
from dx.types.charts.pie import DEXPieChartView
from dx.types.charts.radar_plot import DEXRadarPlotChartView
from dx.types.charts.sankey import DEXSankeyChartView
from dx.types.charts.scatter import DEXScatterChartView
from dx.types.charts.scatterplot_matrix import DEXScatterPlotMatrixChartView
from dx.types.charts.stacked_area import DEXStackedAreaChartView
from dx.types.charts.stacked_percent import DEXStackedPercentChartView
from dx.types.charts.summary import DEXSummaryChartView
from dx.types.charts.sunburst import DEXSunburstChartView
from dx.types.charts.tilemap import DEXTilemapChartView
from dx.types.charts.treemap import DEXTreemapChartView
from dx.types.charts.wordcloud import DEXWordcloudChartView

basic_charts = Annotated[
    Union[
        DEXBarChartView,
        DEXDataPrismChartView,
        DEXLineChartView,
        DEXPieChartView,
        DEXScatterChartView,
        DEXTilemapChartView,
        DEXWordcloudChartView,
    ],
    Field(discriminator="chart_mode"),
]
comparison_charts = Annotated[
    Union[
        DEXBarChartView,
        DEXCorrelationMatrixChartView,
        DEXDotPlotChartView,
        DEXRadarPlotChartView,
        DEXParallelCoordinatesChartView,
        DEXScatterChartView,
        DEXScatterPlotMatrixChartView,
        DEXDivergingBarChartView,
    ],
    Field(discriminator="chart_mode"),
]

time_series_charts = Annotated[
    Union[
        DEXLineChartView,
        DEXCumulativeChartView,
        DEXStackedAreaChartView,
        DEXLinePercentChartView,
        DEXStackedPercentChartView,
        DEXCandlestickChartView,
    ],
    Field(discriminator="chart_mode"),
]

relationship_charts = Annotated[
    Union[
        DEXForceDirectedNetworkChartView,
        DEXSankeyChartView,
        DEXArcDiagramChartView,
        DEXAdjacencyMatrixChartView,
        DEXDendrogramChartView,
    ],
    Field(discriminator="chart_mode"),
]

part_to_whole_charts = Annotated[
    Union[
        DEXPieChartView,
        DEXDonutChartView,
        DEXSunburstChartView,
        DEXTreemapChartView,
        DEXPartitionChartView,
    ],
    Field(discriminator="chart_mode"),
]

funnel_charts = Annotated[
    Union[
        DEXFunnelChartView,
        DEXFunnelChartChartView,
        DEXFunnelTreeChartView,
        DEXFunnelSunburstChartView,
        DEXFlowDiagramChartView,
    ],
    Field(discriminator="chart_mode"),
]

summary_charts = Annotated[
    Union[
        DEXBigNumberChartView,
        DEXWordcloudChartView,
        DEXDimensionMatrixChartView,
        DEXHexbinChartView,
        DEXSummaryChartView,
    ],
    Field(discriminator="chart_mode"),
]

map_charts = Annotated[
    Union[
        DEXChoroplethChartView,
        DEXTilemapChartView,
    ],
    Field(discriminator="chart_mode"),
]
