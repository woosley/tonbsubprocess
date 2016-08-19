import logging
from tornado import gen
from tornado.ioloop import IOLoop
from tonbsuprocess import NonBlockingSubprocess

class SSH(object):
    """ a NonBlocking ssh interface."""
    def __init__(self, host, user, key):
        self.host = host
        self.user = user
        self.key = key
        self.connection_timeout = 2
        self.options = [
            'UserKnownHostsFile /dev/null',
            'StrictHostKeyChecking no',
            'PreferredAuthentications publickey',
            'LogLevel quiet',
            'ConnectTimeout {}'.format(self.connection_timeout)
        ]

    def ssh_cmd(self, cmd):
        ssh_cmd = (
            'ssh {options} -q -T -i "{key}" {user}@{host} <<EOF\n'
            '{cmd}\nEOF\n'.format(
                options=self._optstring(),
                key=self.key,
                user=self.user,
                host=self.host,
                cmd=cmd)
        )
        return ssh_cmd

    @gen.engine
    def run(self, cmd, callback=None):
        cmd = self.ssh_cmd(cmd)
        logging.debug("run ssh command: %s", cmd)
        res = yield gen.Task(NonBlockingSubprocess(cmd).loop)
        callback(res)

    def _optstring(self):
        return ' '.join([
            '-o "{}"'.format(option)
            for option in self.options
        ])
