import unittest
import pandas as pd

from lightweight_charts import Chart


class TestTopBar(unittest.TestCase):
    def test_switcher_fires_event(self):
        chart = Chart()
        chart.topbar.switcher('a', ('1', '2'), func=lambda c: (self.assertEqual(c.topbar['a'].value, '2'), c.exit()))
        chart.run_script(f'{chart.topbar["a"].id}.intervalElements[1].dispatchEvent(new Event("click"))')
        chart.show(block=True)

    def test_button_fires_event(self):
        chart = Chart()
        chart.topbar.button('a', '1', func=lambda c: (self.assertEqual(c.topbar['a'].value, '2'), c.exit()))
        chart.topbar['a'].set('2')
        chart.run_script(f'{chart.topbar["a"].id}.elem.dispatchEvent(new Event("click"))')
        chart.show(block=True)


if __name__ == '__main__':
    unittest.main()
