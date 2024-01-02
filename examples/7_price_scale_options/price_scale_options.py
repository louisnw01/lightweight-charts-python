import pandas as pd
from lightweight_charts import Chart

reset_price_scale = lambda chart: chart.price_scale(auto_scale=True)
invert_price_scale = lambda chart: chart.price_scale(invert_scale=True)
mode_idx_to_100 = lambda chart: chart.price_scale(mode='index100')
visible_off = lambda chart: chart.price_scale(visible=False)
disable_aligned_label = lambda chart: chart.price_scale(align_labels = False)
min_width_to_100 = lambda chart: chart.price_scale(minimum_width = 100)


if __name__ == "__main__":
    df = pd.read_csv(filepath_or_buffer="../1_setting_data/ohlcv.csv")

    chart = Chart()
    chart.set(df)

    chart.topbar.button("Auto", "Auto", func=reset_price_scale)
    chart.topbar.button("Invert", "Invert", func=invert_price_scale)
    chart.topbar.button("Mode to Indexed 100", "Mode to Indexed 100", func=mode_idx_to_100)
    chart.topbar.button("Hide Price Scale", "Price Scale", func=visible_off)
    chart.topbar.button("Disable Align", "Disable Align", func=disable_aligned_label)
    chart.topbar.button("Min Width to 100", "Min Width to 100", func=min_width_to_100)

    chart.show(block=True)
