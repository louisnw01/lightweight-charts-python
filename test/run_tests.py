import unittest

from test_returns import TestReturns
from test_table import TestTable
from test_toolbox import TestToolBox
from test_topbar import TestTopBar
from test_chart import TestChart


TEST_CASES = [
    TestReturns,
    TestTable,
    TestToolBox,
    TestTopBar,
    TestChart,
]

if __name__ == '__main__':
    loader = unittest.TestLoader()
    cases = [loader.loadTestsFromTestCase(module) for module in TEST_CASES]
    suite = unittest.TestSuite(cases)
    unittest.TextTestRunner(verbosity=2).run(suite)