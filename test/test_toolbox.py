import unittest
import pandas as pd

from lightweight_charts import Chart
from util import BARS, Tester

from time import sleep


class TestToolBox(Tester):
    def test_create_horizontal_line(self):
        self.chart.set(BARS)
        horz_line = self.chart.horizontal_line(200, width=4)
        self.chart.show()
        result = self.chart.win.run_script_and_get(f"{horz_line.id}._options");
        self.assertTrue(result)
        self.chart.exit()

    def test_create_trend_line(self):
        self.chart.set(BARS)
        horz_line = self.chart.trend_line(BARS.iloc[-10]['date'], 180, BARS.iloc[-3]['date'], 190)
        self.chart.show()
        result = self.chart.win.run_script_and_get(f"{horz_line.id}._options");
        self.assertTrue(result)
        self.chart.exit()

    def test_create_box(self):
        self.chart.set(BARS)
        horz_line = self.chart.box(BARS.iloc[-10]['date'], 180, BARS.iloc[-3]['date'], 190)
        self.chart.show()
        result = self.chart.win.run_script_and_get(f"{horz_line.id}._options");
        self.assertTrue(result)
        self.chart.exit()

    def test_create_vertical_line(self):
        ...

    def test_create_vertical_span(self):
        ...


if __name__ == '__main__':
    unittest.main()