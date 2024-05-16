import unittest
import pandas as pd
from util import BARS, Tester
from lightweight_charts import Chart


class TestChart(Tester):
    def test_data_is_renamed(self):
        uppercase_df = pd.DataFrame(BARS.copy()).rename({'date': 'Date', 'open': 'OPEN', 'high': 'HIgh', 'low': 'Low', 'close': 'close', 'volUME': 'volume'})
        result = self.chart._df_datetime_format(uppercase_df)
        self.assertEqual(list(result.columns), list(BARS.rename(columns={'date': 'time'}).columns))

    def test_line_in_list(self):
        result0 = self.chart.create_line()
        result1 = self.chart.create_line()
        self.assertEqual(result0, self.chart.lines()[0])
        self.assertEqual(result1, self.chart.lines()[1])


if __name__ == '__main__':
    unittest.main()