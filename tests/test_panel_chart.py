"""Test that the PanelChart works as expected"""
from lightweight_charts.widgets import PanelChart

def test_1_setting_data(ohlcv):
    """The example 1 works"""
    # When
    chart = PanelChart(width=900, height=600)
    chart.set(ohlcv)
    chart.param.trigger("js_load")
    # Then
    assert len(chart._scripts_list) == 4
    assert "makeChart" in chart._scripts_list[0]
    assert ".volumeSeries.setData" in chart._scripts_list[2]
    assert ".candleData =" in chart._scripts_list[3]
    assert not chart._final_scripts

def test_2_live_data(ohlcv, next_ohlcv):
    """The example 2 works"""
    # When
    chart = PanelChart(sizing_mode="stretch_both")
    chart.set(ohlcv)
    chart.param.trigger("js_load")
    
    series = next_ohlcv.iloc[0]
    chart.update(series)
    chart.marker(text="A new price was added")