import time
from tornado import gen
from tornado.testing import AsyncTestCase, gen_test
from tornado.ioloop import IOLoop
from nbsubprocess import NonBlockingSubprocess


class TestSubprocess(NonBlockingSubprocess):
    def __init__(self, cmd):
        self.datalogging = []
        super(TestSubprocess, self).__init__(cmd)

    def log_data(self, data):
        self.datalogging.append([time.time(), data])


class TestPandaSubprocess(AsyncTestCase):

    @gen_test(timeout=10)
    def test_command(self):
        cmd = "echo 1 && sleep 1 && echo 2"
        resobj = yield gen.Task(TestSubprocess(cmd).loop)
        self.assertTrue(len(resobj.datalogging) == 2)

    def get_new_ioloop(self):
        return IOLoop.instance()

    @gen_test(timeout=10)
    def test_multi_commands(self):
        cmds = ['echo 1 && sleep 1 && echo 1.1',
                'echo 2 && sleep 2 && echo 2.2',
                'echo 3 && sleep 3 && echo 3.3']
        gens = [gen.Task(TestSubprocess(i).loop)
                for i in cmds]
        resobjs = yield gens
        self.assertEqual(len(resobjs), 3)
        self.assertEqual(int(resobjs[1].datalogging[-1][0] - resobjs[0].datalogging[-1][0]), 1)
        self.assertEqual(int(resobjs[2].datalogging[-1][0] - resobjs[0].datalogging[-1][0]), 2)
