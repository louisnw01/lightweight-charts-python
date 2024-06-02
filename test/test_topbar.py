import unittest
import pandas as pd

from lightweight_charts import Chart
from util import Tester


class TestTopBar(Tester):
    def test_switcher_fires_event(self):
        self.chart.topbar.switcher('a', ('1', '2'), func=lambda c: (self.assertEqual(c.topbar['a'].value, '2'), c.exit()))
        self.chart.run_script(f'{self.chart.topbar["a"].id}.intervalElements[1].dispatchEvent(new Event("click"))')
        self.chart.show(block=True)

    def test_button_fires_event(self):
        self.chart.topbar.button('a', '1', func=lambda c: (self.assertEqual(c.topbar['a'].value, '2'), c.exit()))
        self.chart.topbar['a'].set('2')
        self.chart.run_script(f'{self.chart.topbar["a"].id}.elem.dispatchEvent(new Event("click"))')
        self.chart.show(block=True)


if __name__ == '__main__':
    unittest.main()
