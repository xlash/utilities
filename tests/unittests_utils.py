import logging
import unittest
import datetime
import os
# from os import path
# import sys
import commands as cmds
import re
import random
# # To support relative module import
# if __name__ == '__main__':
#     sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utilities import utils as u
from utilities import test_utilities as tu


class OptionsTest(u.Options):
    def __init__(self, params):
        super(OptionsTest, self).__init__(params)


class TestOptionsClass(unittest.TestCase):

    def test_Options_empty_value(self):
        o = u.Options({})
        self.assertEqual(o.debug, False)
        self.assertEqual(o._debug, False)
        self.assertEqual(o.is_debug, False)
        o.debug = True
        self.assertEqual(o.debug, True)
        self.assertEqual(o._debug, True)
        self.assertEqual(o.is_debug, True)
        self.assertEqual(o.testval, None)
        o.testval = 54
        self.assertEqual(o.testval, 54)
        self.assertEqual(o.is_silent, False)
        o.is_silent = True
        self.assertEqual(o.is_silent, True)

    def test_Options_iterable(self):
        """Test the iterable object"""
        o = u.Options({'1': True, '2': False, '3': True})
        for i in o:
            if len(i) == 1 and int(i) % 2 == 1:
                self.assertEqual(o[i], True)
                self.assertNotEqual(o[i], False)
            elif len(i) == 1:
                self.assertEqual(o[i], False)
                self.assertNotEqual(o[i], True)

    def test_Options_with_values(self):
        o = u.Options({'is_silent': True, 'debug': True, 'testval': 58})
        self.assertEqual(o.debug, True)
        self.assertEqual(o._debug, True)
        self.assertEqual(o.is_debug, True)
        o.debug = False
        self.assertEqual(o.debug, False)
        self.assertEqual(o._debug, False)
        self.assertEqual(o.is_debug, False)
        self.assertEqual(o.testval, 58)
        o.testval = 54
        self.assertEqual(o.testval, 54)
        self.assertEqual(o.is_silent, True)
        o.is_silent = False
        self.assertEqual(o.is_silent, False)

    def test_Options_with_nonbool(self):
        o = u.Options({'debug': True, 'testval': 58})
        try:
            o.is_silent = 54
        except AttributeError:
            pass
        self.assertEqual(o.is_silent, False)

    def test_Options_from_Options(self):
        o = u.Options({'debug': True, 'testval': 58})
        o2 = u.Options(o)
        self.assertEqual(o.is_silent, o2.is_silent)
        self.assertEqual(o.testval, o2.testval)
        self.assertEqual(o.debug, o2.debug)

    def test_Options_kwargs(self):
        o = u.Options({'debug': True, 'testval': 58},
                      is_test_kwargs=True, rocknroll=2)
        self.assertEqual(o['is_silent'], False)
        self.assertEqual(o['testval'], 58)
        self.assertEqual(o['debug'], True)
        self.assertEqual(o['is_test_kwargs'], True)
        self.assertEqual(o['rocknroll'], 2)

    def test_Options_subscriptable(self):
        o = u.Options({'debug': True, 'testval': 58})
        self.assertEqual(o['is_silent'], False)
        self.assertEqual(o['testval'], 58)
        self.assertEqual(o['debug'], True)

    def test_multipleOptions(self):
        o1 = u.Options({'debug': True, 'testval': 58})
        o2 = u.Options({'debug': False, 'testval': 60})
        self.assertEqual(o1['is_silent'], False)
        self.assertEqual(o1['testval'], 58)
        self.assertEqual(o1['debug'], True)
        self.assertEqual(o2['is_silent'], False)
        self.assertEqual(o2['testval'], 60)
        self.assertEqual(o2['debug'], False)

    def test_Options_with_None(self):
        o = u.Options(None)
        self.assertEqual(o.debug, False)
        self.assertEqual(o._debug, False)
        self.assertEqual(o.is_debug, False)
        o.debug = True
        self.assertEqual(o.debug, True)
        self.assertEqual(o._debug, True)
        self.assertEqual(o.is_debug, True)
        self.assertEqual(o.testval, None)
        o.testval = 54
        self.assertEqual(o.testval, 54)
        self.assertEqual(o.is_silent, False)
        o.is_silent = True
        self.assertEqual(o.is_silent, True)

    def test_inheritance(self):
        o1 = OptionsTest({'debug': True, 'testval': 58})
        o2 = OptionsTest({'debug': False, 'testval': 60})
        self.assertEqual(o1['is_silent'], False)
        self.assertEqual(o1['testval'], 58)
        self.assertEqual(o1['debug'], True)
        self.assertEqual(o2['is_silent'], False)
        self.assertEqual(o2['testval'], 60)
        self.assertEqual(o2['debug'], False)

    def test_prefix_num_n_dict_n_array(self):
        o1 = OptionsTest({'debug': True, 'testval': 58})
        self.assertEqual(o1['is_silent'], False)
        self.assertEqual(o1['num_test'], 0)
        self.assertEqual(o1['list_test'], [])
        self.assertEqual(o1['dict_test'], {})
        o1.num_test = 10
        o1.list_test = [1, 2, 3]
        o1.dict_test = {'a': 1, 'b': 2}
        self.assertEqual(o1['num_test'], 10)
        self.assertEqual(o1['list_test'], [1, 2, 3])
        self.assertEqual(o1['dict_test'], {'a': 1, 'b': 2})

    def test_prefix_errors(self):
        o1 = OptionsTest({'debug': True, 'testval': 58})
        self.assertRaises(AttributeError, o1.__setattr__,
                          'num_test', '127.0.0.1')
        self.assertRaises(AttributeError, o1.__setattr__,
                          'list_test', '127.0.0.1')
        self.assertRaises(AttributeError, o1.__setattr__,
                          'dict_test', '127.0.0.1')
        self.assertRaises(AttributeError, o1.__setattr__,
                          'is_test', '127.0.0.1')


class TestUtilsModule(unittest.TestCase):
    def test_find_line_number_for_x_min_ago(self):
        self.assertEqual(u.find_line_number_for_x_min_ago(
            tu.get_fixture_path('.utils.unittest.ltm_log_1.data'),
            10, datetime.datetime(2016, 3, 11, 4, 12)), 7392)
        self.assertEqual(u.find_line_number_for_x_min_ago(
            tu.get_fixture_path('.utils.unittest.ltm_log_1.data'),
            10, datetime.datetime(2016, 3, 10, 22, 12)), 5548)
        self.assertEqual(u.find_line_number_for_x_min_ago(
            tu.get_fixture_path('.utils.unittest.ltm_log_1.data'),
            10, datetime.datetime(2016, 3, 10, 4, 12)), -1)

    def test_dt_convert_to_utc_tzunaware(self):
        x = u.convert_dt_to_utc_dt(datetime.datetime.now())
        self.assertEqual(x.tzinfo.__class__.__name__, 'UTC')
    # def test_dt_convert_to_utc_tzaware(self):
    #     x=u.convert_dt_to_utc_dt(datetime.datetime.now(tzinfo))
    #     self.assertEqual(x.tzinfo.__class__.__name__,'UTC')


class Add(object):

    def __init__(self, val1, val2):
        self.results = int(val1) + int(val2)


class Test_HostFileClass(unittest.TestCase):
    def setUp(self):
        pass

    def test_1(self):
        filename = tu.get_fixture_path("hostsfile_test1")
        _h = u.Hosts(filename)
        self.assertRaises(u.HostNonDefined, _h.__getattr__,
                          'invalidname.localdomain')
        self.assertRaises(u.HostNonDefined, _h.__getattr__,
                          '127.0.0.10')
        self.assertEqual(_h['localhost.localdomain'], '127.0.0.1')
        self.assertEqual(_h['localhost1.localdomain'], '127.0.0.2')
        self.assertNotEqual(_h['localhost2.localdomain'], '127.0.0.2')
        self.assertEqual(_h['F5-LTM1A=blade1'], '127.0.0.7')
        self.assertEqual(_h['alternate.localhost1.localdomain'], '127.0.0.2')
        self.assertEqual(_h['127.0.0.7'], ['F5-LTM1A=BLADE1'])
        self.assertEqual(_h['127.0.0.7'], ['F5-LTM1A=BLADE1'])

    def test_invalidHostFile(self):
        self.assertRaises(IOError, u.Hosts, 'invalidfilename')

    def test_str(self):
        hostsData = """
#Hosts file fixture for testing
127.0.0.1   localhost.localdomain   #"Description of equipment"  Equipment_type
127.0.0.2   localhost1.localdomain,alternate.localhost1.localdomain #"Description of equipment1"  Equipment_type
127.0.0.3   localhost2.localdomain  #"Description of equipment2"  Equipment_type
127.0.0.4   localhost3.localdomain  #"Description of equipment3"  Equipment_type
127.0.0.4   localhost1-type1.localdomain    #"Description of equipment4"  Equipment_type
127.0.0.5   localhost2-type1.localdomain    #"Description of equipment4"  Equipment_type
127.0.0.6   localhost3-type1.localdomain    #"Description of equipment4"  Equipment_type
127.0.0.7   F5-LTM1A=blade1 #"Description of equipment5"  Equipment_type
"""
        _h = u.Hosts(hostsData)
        self.assertRaises(u.HostNonDefined, _h.__getattr__,
                          'invalidname.localdomain')
        self.assertRaises(u.HostNonDefined, _h.__getattr__,
                          '127.0.0.10')
        self.assertEqual(_h['localhost.localdomain'], '127.0.0.1')
        self.assertEqual(_h['localhost1.localdomain'], '127.0.0.2')
        self.assertNotEqual(_h['localhost2.localdomain'], '127.0.0.2')
        self.assertEqual(_h['F5-LTM1A=blade1'], '127.0.0.7')
        self.assertEqual(_h['alternate.localhost1.localdomain'], '127.0.0.2')
        self.assertEqual(_h['127.0.0.7'], ['F5-LTM1A=BLADE1'])


class Test_intelligent_file_parsing_for(unittest.TestCase):
    def test_unit_intelligent_file_parsing_for(self):
        # FIXME 2016-04-29 GuillaumeNM not a valid test case yet
        cmd = 'lib/file_seek.py -o START_BYTE -l DELTA_BYTE FILENAME '
        file = tu.get_fixture_path("hostsfile_test1")
        x = u.intelligent_file_parsing_for(cmd, file, 'test1',
                                               {'debug': False})
        # res = x.get_currentresults()
        # expected = ('Hosts file fixture for testing\n127.0.0.1 \t'
        #            'localhost.localdomain\t#"Description of equipment"'
        #            '  Equipment_type\n127.0.0.2 \tlocalhost1.localdomain'
        #            '\talternate.localhost1.localdomain #"Description of '
        #            'equipment1"  Equipment_type\n127.0.0.3 \tlocalhost2.'
        #            'localdomain \t#"Description of equipment2"  Equipment'
        #            '_type\n127.0.0.4 \tlocalhost3.localdomain\t#"Descript'
        #            'ion of equipment3"  Equipment_type\n127.0.0.4 \tlocal'
        #            'host1-type1.localdomain\t#"Description of equipment4"'
        #            '  Equipment_type\n127.0.0.5 \tlocalhost2-type1.locald'
        #            'omain\t#"Description of equipment4"  Equipment_type\n'
        #            '127.0.0.6 \tlocalhost3-type1.localdomain\t#"Descripti'
        #            'on of equipment4"  Equipment_type\n127.0.0.7 \tF5-LTM'
        #            '1A=blade1\t#"Description of equipment5"  Equipment_ty'
        #            'pe\n')
        # self.assertEqual(res, expected)
        # ###CALCULATE RESULTS
        results_hash = {'test1': 'successful'}
        # ########UPDATE RESULTS
        x.update_results(results_hash)
        self.assertEqual(x.get_results(), results_hash)
        cmd = (tu.LIBPATH + '/file_seek.py -o START_BYTE -l '
               'DELTA_BYTE FILENAME ')
        file = tu.get_fixture_path("hostsfile_test1")
        y = u.intelligent_file_parsing_for(cmd, file, 'test1',
                                               {'debug': False})
        self.assertEqual(y.get_results(), results_hash)
        # No new content added to the file
        self.assertEqual(y.get_currentresults(), '')
        results_hash = {'test1': 'successful', 'test2': 'suckitupcoconut'}
        y.update_results(results_hash)
        self.assertEqual(y.get_results(), results_hash)
        cmd = (tu.LIBPATH + '/file_seek.py -o START_BYTE -l '
               'DELTA_BYTE FILENAME ')
        file = tu.get_fixture_path("hostsfile_test1")
        z = u.intelligent_file_parsing_for(cmd, file, 'test1',
                                               {'debug': False})
        # No new content added to the file
        self.assertEqual(z.get_currentresults(), '')
        self.assertEqual(z.get_results(), results_hash)
        self.assertRaises(AssertionError, self.assertEqual,
                          z.get_results(), {})

    def unit_test_monitor_over_time():
        if u.is_F5():
            x = u.monitor_over_time('tmsh -q show net rst-cause', 10, 2,
                                        'net.rst-cause.'+str(10)+'min',
                                        {"debug": True})
            x.get_results()
            res = x.get_currentresults()
            results = {}
            for line in res.splitlines():
                # Match rst-cause line like
                # APM HTTP body too big                             29
                if re.match("[A-Za-z].+[0-9]+", line) is not None:
                    count = int(line.split(' ')[-1])
                    rst_cause = (" ").join(line.split(' ')[0:-1]).rstrip(" ")
                    results[rst_cause] = count
            x.write_results_if_required(results)


class Test_Logger(unittest.TestCase):
    def test_logger_1(self):
        # Repeating tests cases is important for a toggle function
        self.assertFalse(u.Logger.toggle_debug(level=logging.CRITICAL))
        self.assertFalse(u.Logger.toggle_debug(level=logging.CRITICAL))
        self.assertFalse(u.Logger.toggle_debug(level=logging.CRITICAL))
        self.assertFalse(u.Logger.toggle_debug(level=logging.CRITICAL))
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug(level=logging.INFO))
        self.assertFalse(u.Logger.toggle_debug(level=logging.INFO))
        self.assertFalse(u.Logger.toggle_debug(level=logging.INFO))
        self.assertFalse(u.Logger.toggle_debug(level=logging.INFO))
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug(level=logging.DEBUG))
        self.assertTrue(u.Logger.toggle_debug(level=logging.DEBUG))
        self.assertTrue(u.Logger.toggle_debug(level=logging.DEBUG))
        self.assertTrue(u.Logger.toggle_debug(level=logging.DEBUG))
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())
        self.assertTrue(u.Logger.toggle_debug())
        self.assertFalse(u.Logger.toggle_debug())


class Test_general(unittest.TestCase):
    def test_string_apply_case(self):
        self.assertEqual(u.string_apply_case('aaAAA', 'BBBBB'), 'bbBBB')
        self.assertEqual(u.string_apply_case('aaAAA', 'aBaAA'), 'abAAA')
        self.assertEqual(u.string_apply_case('aaA', 'aBaAA'), 'abA')


class Test_update_progress(unittest.TestCase):
    def test_update_progress(self):
        for i in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            u.update_progress(i, 'Test Progress')


class Test_Application(unittest.TestCase):
    def test_application_creation(self):
        app = u.Application(version=1.2, buildDate='1111-11-11')
        self.assertEqual(app.getVersion(), 'VERSION=1.2 BUILD_DATE=1111-11-11')
        self.assertEqual(app.name, 'u.unittests')

# testApplication.py not found. Removed
# class Test_ApplicationModule(unittest.TestCase):
#     def test_applicationModule_loadup(self):
#         import testApplication
#         testApplication.testApplication()

# testApplication.py not found. Removed
#     def test_applicationModule_exportImport(self):
#         import testApplication
#         testApplication.testApplication()
#         chosenNum = random.randint(0, 10000)
#         testApplication.app.settings.randomNum = chosenNum
#         testApplication.app.saveSettings()
#         testApplication.app.settings.randomNum = random.randint(0, 10000)
#         self.assertNotEqual(testApplication.app.settings.randomNum, chosenNum)
#         testApplication.app.loadSettings()
#         self.assertEqual(testApplication.app.settings.randomNum, chosenNum)


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


class Test_PythonVersion(unittest.TestCase):
    def test_version_under(self):
        res = u.pythonVersionMin(2, 11, raiseIfNotMet=False,
                                     majorVersionMustMatch=True,
                                     description='test_version_under')
        self.assertFalse(res)

    def test_version_ok(self):
        res = u.pythonVersionMin(0, 0, raiseIfNotMet=False,
                                     majorVersionMustMatch=False,
                                     description='test_version_ok')
        self.assertTrue(res)

    def test_version_incorrectMV(self):
        # Python 2.4 syntax
        try:
            u.pythonVersionMin(0, 0, raiseIfNotMet=True,
                                   majorVersionMustMatch=True,
                                   description='test_version_incorrectMV')
        except u.PyVersionError:
            pass

    def test_version_incorrectV(self):
        # Python 2.4 syntax
        try:
            u.pythonVersionMin(4, 0, raiseIfNotMet=True,
                                   majorVersionMustMatch=False,
                                   description='test_version_incorrectV')
        except u.PyVersionError:
            pass


class Test_Unique(unittest.TestCase):
    def test_simple(self):
        res = u.unique([1, 2, 3, 1, 2, 3, 1, 2, 3])
        self.assertEqual([1, 2, 3], res)

    def test_objects(self):
        res = u.unique([datetime.datetime(2015, 5, 1),
                            datetime.datetime(2015, 5, 1),
                            datetime.datetime(2015, 5, 1),
                            datetime.datetime(2015, 6, 1)],
                            objectCompare=True)
        self.assertEqual(len(res), 2)

@u.accepts(a=int,b=list,c=(str,unicode))
def testAccepts(a,b=None,c=None):
    return 'ok'


class customException(Exception):
    pass

@u.accepts(customException, a=int, b=list, c=(str, unicode))
def testAccepts2(a, b=None, c=None):
    return 'ok'


class AcceptTest(object):

    @u.accepts(customException, self=object, a=int, b=list, c=(str, unicode))
    def __init__(self, a, b=None, c=None):
        self.i = 'ok'

    @u.accepts(customException, self=object, plusThis='AcceptTest')
    def add(self, plusThis):
        return 'added'

class Test_accepts_decorator(unittest.TestCase):

    def test_globalMethod(self):
        with self.assertRaises(u.ArgTypeException):
            testAccepts(13, c=[], b='df')
        self.assertEqual(testAccepts(13, b=[], c='df'), 'ok')

    def test_customException(self):
        with self.assertRaises(customException):
            testAccepts2(13, c=[], b='df')
        self.assertEqual(testAccepts2(13, b=[], c='df'), 'ok')

    def test_class_init(self):
        a = AcceptTest(13, b=[], c='df')
        self.assertEqual(a.i, 'ok')
        with self.assertRaises(customException):
            b = AcceptTest(13, b=None, c='df')
        c = AcceptTest(15, b=[], c='df')
        self.assertEqual(a.add(c), 'added')
        with self.assertRaises(customException):
            a.add(1)




if __name__ == '__main__':
    u.Application()
    unittest.main()
