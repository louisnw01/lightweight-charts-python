import unittest
import pandas as pd

from lightweight_charts import Chart


BARS = pd.read_csv('../examples/1_setting_data/ohlcv.csv')



class Tester(unittest.TestCase):
    def setUp(self):
        self.chart: Chart = Chart(100, 100, 800, 100);

    def tearDown(self) -> None:
        self.chart.exit()




