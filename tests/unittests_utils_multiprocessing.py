import unittest
import logging
import os
import time
import sys
from os import path

# To support relative module import
if __name__ == '__main__' and __package__ is None:
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import test_utilities
import utils


logGod = utils.Logger(__name__)
logger = logGod.logger()


class Result(object):
    def __init__(self, startAt=0):
        self._results = []
        self.i = startAt

    def update(self, i=1):
        self._results.append(i)
        # print "pid=%s update i=%s" % (os.getpid(), self.i)
        self.i += i
        time.sleep(0.001)

    def get_results(self):
        return self._results


def simple_test(work_unit, orchestrator, **kwargs):
    orchestrator.update(1)
    logger.info("Process id=%s i=%s completed! " % (os.getpid(), 1))


def cpu_bound_test(work_unit, orchestrator, **kwargs):
    # if args.__class__.__name__!='list' or len(args)!=2:
    #       #logger.error("Invalid parameters given to worker method")
    #       print "Invalid parameters given to worker method"
    # work_unit,options = args
    i = work_unit
    # print "cpu_bound_test:" +str(orchestrator)
    # print "cpu_bound_test:" +str(**kwargs)
    j = i
    while j < 10000000:
        j += 1
        # time.sleep(0.01)
    orchestrator.update(i)
    logger.debug("Thread i=%s completed! " % (i))


class Test_performance_multithreaded(unittest.TestCase):
    def setUp(self):
        utils.MultiprocessingManager.register('Result', Result)
        self.multiprocessing_manager = utils.Manager()
        logger.info("Test %s " % (utils.function_get_current_name()))

    def test_cpubound_task_multiprocess_signal_handling(self):
        logger.info('Test case needs to be run manually. Press CTRL+X while '
                    'running the other tests')

    def test_cpubound_task_multithread_signal_handling(self):
        logger.info('Test case needs to be run manually. Press CTRL+X while'
                    ' running the other tests')

    def test_cpubound_task_multiprocess(self):
        utils.MultiprocessingManager.register('Result', Result)
        # multiprocessing_manager = utils.Manager()
        results = self.multiprocessing_manager.Result()
        output = utils.work_in_parallel(cpu_bound_test, range(0, 99),
                                        args=(results,), num_thread=8,
                                        is_cpu_bounded=True,
                                        is_benchmarked=True)
        res = results.get_results()
        # Validation
        for i in range(0, 99):
            self.assertIn(i, res)
        self.assertEqual(len(res), 99)
        # Ensure it took at most 30 seconds
        self.assertGreater(30, output['time'])

    def test_cpubound_task_multithread(self):
        results = self.multiprocessing_manager.Result()
        output = utils.work_in_parallel(cpu_bound_test, range(0, 9),
                                        args=(results,), num_thread=8,
                                        is_cpu_bounded=False,
                                        is_benchmarked=True)
        res = results.get_results()
        # Validation
        for i in range(0, 9):
            self.assertIn(i, res)
        self.assertEqual(len(res), 9)
        # Ensure it took at most 30 seconds
        self.assertGreater(30, output['time'])

    def test_manager_multiprocess_update(self):
        results = self.multiprocessing_manager.Result(startAt=10)
        results.get_results()
        output = utils.work_in_parallel(simple_test, range(0, 1000),
                                        args=(results,), num_thread=8,
                                        is_cpu_bounded=True,
                                        is_benchmarked=True)
        logger.debug("Test %s output=%s"
                     % (utils.function_get_current_name(),
                        output))
        self.assertEqual(1000, len(results.get_results()))

    # def donot_test_1(self):
    #     for k in range(1, 10):
    #         try:
    #             start = time.time()
    #             pool = Pool(k,init_worker)
    #             results.results = pool.map_async(cpu_bound_test,range(0, 9)).get(9999999)
    #             end = time.time()
    #             print "Time threads=%s time=%s" % (k, end - start)
    #         except KeyboardInterrupt:
    #             print "So disappointed of you.... Go CTRL+C yourself ! "
    #             pool.terminate()
    #             pool.join()
    #             break
    #     results = work_in_parallel(test, range(0, 9),
    #                                num_thread=4, is_cpu_bounded=True,
    #                                i='allo')
    #     print str(results.results)

if __name__ == '__main__':
    logGod, logger = test_utilities.parse_params()
    #_debug = utils.toggle_debug(level = logging.DEBUG)
    sys.exit(unittest.main())
