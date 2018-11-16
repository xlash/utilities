import logging
import random
import os
import sys
import unittest
# If launched manually, not via unittest or nose
if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utilities import utils3_5 as u
from utilities import test_utilities as tu
import testApplication


class Test_Application(unittest.TestCase):
    def test_application_creation(self):
        app = u.Application(version=1.2, buildDate='1111-11-11')
        self.assertEqual(app.getVersion(), 'VERSION=1.2 BUILD_DATE=1111-11-11')
        self.assertEqual(app.name, 'unittests_application')


# testApplication.py not found. Removed
class Test_ApplicationModule(unittest.TestCase):

    def test_applicationModule_loadup(self):
        with self.assertRaises(SystemExit) as cm:
            testApplication.testApplication()
        self.assertEqual(cm.exception.code, 2)

    def test_applicationModule_exportImport(self):
        testApp = testApplication.testApplication2()
        chosenNum = random.randint(0, 10000)
        testApp.app.settings.randomNum = chosenNum
        testApp.app.saveSettings()
        testApp.app.settings.randomNum = random.randint(0, 10000)
        self.assertNotEqual(testApp.app.settings.randomNum, chosenNum)
        testApp.app.loadSettings()
        self.assertEqual(testApp.app.settings.randomNum, chosenNum)


# testApplication.py not found. Removed
# class Test_ApplicationScript(unittest.TestCase):
#     def test_application_script(self):
#         # print __file__
#         status, output = cmds.getstatusoutput('python %s/testApplication.py'
#                                               % (os.path.dirname(__file__)))
#         postWarningResult = output.splitlines()[-1]
#         self.assertEqual(postWarningResult, 'testApplication')
#         self.assertEqual(status, 0)

#         status, output = cmds.getstatusoutput('python %s/testApplication.py -V'
#                                               % (os.path.dirname(__file__)))
#         postWarningResult = output.splitlines()[-1]
#         self.assertEqual(postWarningResult, 'VERSION=0.1 '
#                                             'BUILD_DATE=2016-06-08')
#         self.assertEqual(status, 0)

#         status, output = cmds.getstatusoutput('python %s/testApplication.py -h'
#                                               % (os.path.dirname(__file__)))
#         expectedResult = """usage: testApplication.py [-h] [-v] [-V] [-t]

# optional arguments:
#   -h, --help     show this help message and exit
#   -v, --verbose  increase output verbosity...repeat up to 3x (-vvv) for
#                  WARNING,==>INFO==>DEBUG.
#   -V, --version  Returns the program version
#   -t, --tests    test entry, optionnal"""
#         self.assertEqual(output, expectedResult)
#         self.assertEqual(status, 0)


if __name__ == '__main__':
    u.Application()
    unittest.main()
