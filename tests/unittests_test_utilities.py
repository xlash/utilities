import time
import unittest
import sys
from os import path
# To support relative module import
if __name__ == '__main__' and __package__ is None:
    path_lib = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(path_lib)

from lib import utils
from lib import test_utilities as tu

# FIXME GuillaumeNM 2016-04 Build test method for get_obfuscate_bitswise()


class TestFileSeek(unittest.TestCase):
    def setUp(self):
        pass

    def test_performance_ok(self):
            with tu.EnsurePerformance('Test', 1.1):
                time.sleep(1)

    def test_performance_failed(self):
        with self.assertRaises(tu.PerformanceException):
            with tu.EnsurePerformance('Test', 1):
                time.sleep(1)

if __name__ == '__main__':
    app = utils.Application(description='Test utilities unittests',
                            version=0.1, buildDate='2016-06',
                            author='GuillaumeNM')
    app.start()
    logger = app.logger
    unittest.main()
