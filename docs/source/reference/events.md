# `Events`

````{py:class} AbstractChart.Events
The chart events class, accessed through `chart.events`

Events allow asynchronous and synchronous callbacks to be passed back into python.

Chart events can be subscribed to using: `chart.events.<name> += <callable>`

```{py:method} search -> (chart: Chart, string: str)
Fires upon searching. Searchbox will be automatically created.

```

```{py:method} new_bar -> (chart: Chart)
Fires when a new candlestick is added to the chart.

```

```{py:method} range_change -> (chart: Chart, bars_before: NUM, bars_after: NUM)
Fires when the range (visibleLogicalRange) changes.

```

````

Tutorial: [Topbar & Events](../tutorials/events.md)

