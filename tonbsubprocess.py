""" NonBlockingSubprocess: the nonblocking subprocess for tornado.
Usage:
    res = yield gen.Task(NonBlockingSubprocess(cmd).loop)
    result = res.gather_response()
    print result['data']
    print result['success']

Those attributes are saved for later usages:
    cmd: command line
    data: command output
    start_time: start timestamp of the command
    end_time: end timestamp of the command
    pipe: the subprocess.Popen() object, which can be used for getting the
    return code of the command

You can also inherit from class NonBlockingSubprocess and write your own
function log_data, it is called when reading data from subprocess output

    def log_data(self, data):
        print data

"""

import subprocess
import fcntl
import os
import functools
import time
from tornado.ioloop import IOLoop


class NonBlockingSubprocess(object):
    """A non blocking subprocess handler"""

    def __init__(self, cmd, ioloop=None):

        self.start_time = time.time()
        self.pipe = subprocess.Popen(cmd,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     close_fds=True)
        self.cmd = cmd
        self.ioloop = ioloop or IOLoop.current()
        self.data = ""

    def loop(self, callback=None):

        # make the filehandlers non-blocking
        # do not use stdout.fileno() here
        fh = self.pipe.stdout
        fl = fcntl.fcntl(fh, fcntl.F_GETFL)
        fcntl.fcntl(fh, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        self.fh = fh

        # you must have a callback here
        fd_callback = functools.partial(self.__poll_handler, callback=callback)
        self.ioloop.add_handler(fh.fileno(), fd_callback, self.ioloop.READ)

    def __poll_handler(self, fd, event, callback=None):
        if self.pipe.poll() is not None:
            # event finished
            self.ioloop.remove_handler(fd)
            data = self.pipe.stdout.read()
            if len(data) > 0:
                self.log_data(data)
                self.data += data
            self.end_time = time.time()

            # and you have to set the callback here!
            # return the class for later usage
            callback(self)

        data = ""
        while True:
            try:
                data = os.read(fd, 512)
                if len(data) == 0:
                    # command finished
                    break
                else:
                    self.data += data
                    self.log_data(data)
            # OSError: [Errno 11] Resource temporarily unavailable
            except OSError as e:
                break

    def log_data(self, data):
        """ used for logging cmd output in realtime. """
        pass

    def gather_response(self):
        """ gather response from NonBlockingSubprocess object. """

        res = {}
        res['returncode'] = self.pipe.returncode
        res['cmd'] = self.cmd
        res['data'] = self.data
        res['start_time'] = self.start_time
        res['end_time'] = self.end_time
        res['success'] = True if res['returncode'] == 0 else False
        res['pid'] = self.pipe.pid
        res['reason'] = "command returned {}".format(res['returncode'])
        return res
