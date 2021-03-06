"""
//  -------------------------------------------------------------
//  author        Giga
//  project       qeeqbox/honeypots
//  email         gigaqeeq@gmail.com
//  description   app.py (CLI)
//  licensee      AGPL-3.0
//  -------------------------------------------------------------
//  contributors list qeeqbox/social-analyzer/graphs/contributors
//  -------------------------------------------------------------
"""

from uuid import uuid4
from honeypots.helper import close_port_wrapper, get_free_port, kill_server_wrapper, server_arguments, setup_logger, disable_logger
from os import path
from subprocess import Popen
from twisted.python import log as tlog
from redis import StrictRedis
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from warnings import filterwarnings
filterwarnings(action='ignore', module='.*OpenSSL.*')


class QRedisServer():
    def __init__(self, ip=None, port=None, username=None, password=None, mocking=False, config=''):
        self.ip = ip or '0.0.0.0'
        self.port = port or 6379
        self.username = username or "test"
        self.password = password or "test"
        self.mocking = mocking or ''
        self.process = None
        self.uuid = 'honeypotslogger'
        self.config = config
        if config:
            self.logs = setup_logger(self.uuid, config)
        else:
            self.logs = setup_logger(self.uuid, None)
        disable_logger(1, tlog)

    def redis_server_main(self):
        _q_s = self

        class CustomRedisProtocol(Protocol):

            def get_command(self, data):
                try:
                    _data = data.decode('utf-8').split('\x0d\x0a')
                    if _data[0][0] == "*":
                        _count = int(_data[0][1]) - 1
                        _data.pop(0)
                        if _data[0::2][0][0] == "$" and len(_data[1::2][0]) == int(_data[0::2][0][1]):
                            return _count, _data[1::2][0]
                except Exception as e:
                    print(e)

                return 0, ""

            def parse_data(self, c, data):
                _data = data.decode('utf-8').split('\r\n')[3::]
                user, password = "", ""
                if c == 2:
                    _ = 0
                    if _data[0::2][_][0] == "$" and len(_data[1::2][_]) == int(_data[0::2][_][1]):
                        user = (_data[1::2][_])
                    _ = 1
                    if _data[0::2][_][0] == "$" and len(_data[1::2][_]) == int(_data[0::2][_][1]):
                        password = (_data[1::2][_])
                if c == 1:
                    _ = 0
                    if _data[0::2][_][0] == "$" and len(_data[1::2][_]) == int(_data[0::2][_][1]):
                        password = (_data[1::2][_])
                if c == 2 or c == 1:
                    if user == _q_s.username and password == _q_s.password:
                        _q_s.logs.info({'server': 'redis_server', 'action': 'login', 'status': 'success', 'ip': self.transport.getPeer(
                        ).host, 'port': self.transport.getPeer().port, 'username': _q_s.username, 'password': _q_s.password})
                    else:
                        _q_s.logs.info({'server': 'redis_server', 'action': 'login', 'status': 'failed', 'ip': self.transport.getPeer(
                        ).host, 'port': self.transport.getPeer().port, 'username': user, 'password': password})

            def connectionMade(self):
                self._state = 1
                self._variables = {}
                _q_s.logs.info({'server': 'redis_server', 'action': 'connection', 'ip': self.transport.getPeer(
                ).host, 'port': self.transport.getPeer().port})

            def dataReceived(self, data):
                c, command = self.get_command(data)
                if command == "AUTH":
                    self.parse_data(c, data)
                    self.transport.write(b"-ERR invalid password\r\n")
                else:
                    self.transport.write(
                        b"-ERR unknown command '{}'\r\n".format(command))
                self.transport.loseConnection()

        factory = Factory()
        factory.protocol = CustomRedisProtocol
        reactor.listenTCP(port=self.port, factory=factory,
                          interface=self.ip)
        reactor.run()

    def run_server(self, process=False, auto=False):
        if process:
            if auto:
                port = get_free_port()
                if port > 0:
                    self.port = port
                    self.process = Popen(['python3', path.realpath(__file__), '--custom', '--ip', str(self.ip), '--port', str(self.port), '--username', str(
                        self.username), '--password', str(self.password), '--mocking', str(self.mocking), '--config', str(self.config), '--uuid', str(self.uuid)])
                    if self.process.poll() is None:
                        self.logs.info({'server': 'redis_server', 'action': 'process', 'status': 'success',
                                        'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
                    else:
                        self.logs.info({'server': 'redis_server', 'action': 'process', 'status': 'error',
                                        'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
                else:
                    self.logs.info({'server': 'redis_server', 'action': 'setup', 'status': 'error',
                                    'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
            elif self.close_port() and self.kill_server():
                self.process = Popen(['python3', path.realpath(__file__), '--custom', '--ip', str(self.ip), '--port', str(self.port), '--username', str(
                    self.username), '--password', str(self.password), '--mocking', str(self.mocking), '--config', str(self.config), '--uuid', str(self.uuid)])
                if self.process.poll() is None:
                    self.logs.info({'server': 'redis_server', 'action': 'process', 'status': 'success',
                                    'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
                else:
                    self.logs.info({'server': 'redis_server', 'action': 'process', 'status': 'error',
                                    'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
        else:
            self.redis_server_main()

    def test_server(self, ip=None, port=None, username=None, password=None):
        try:
            _ip = ip or self.ip
            _port = port or self.port
            _username = username or self.username
            _password = password or self.password
            r = StrictRedis.from_url(
                'redis://{}:{}@{}:{}/1'.format(_username, _password, _ip, _port))
            for key in r.scan_iter("user:*"):
                pass
        except BaseException:
            pass

    def close_port(self):
        ret = close_port_wrapper('redis_server', self.ip, self.port, self.logs)
        return ret

    def kill_server(self):
        ret = kill_server_wrapper('redis_server', self.uuid, self.process)
        return ret


if __name__ == '__main__':
    parsed = server_arguments()
    if parsed.docker or parsed.aws or parsed.custom:
        qredisserver = QRedisServer(ip=parsed.ip, port=parsed.port, username=parsed.username,
                                    password=parsed.password, mocking=parsed.mocking, config=parsed.config)
        qredisserver.run_server()
