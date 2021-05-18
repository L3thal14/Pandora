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
from ftplib import FTP as FFTP
from twisted.python import log as tlog
from twisted.internet import reactor
from twisted.protocols.ftp import FTPFactory, FTP, AUTH_FAILURE
from warnings import filterwarnings
filterwarnings(action='ignore', module='.*OpenSSL.*')


class QFTPServer():
    def __init__(self, ip=None, port=None, username=None, password=None, mocking='', config=''):
        self.ip = ip or '0.0.0.0'
        self.port = port or 21
        self.username = username or 'test'
        self.password = password or 'test'
        self.mocking = mocking or ''
        self.random_servers = ['ProFTPD 1.2.10', 'ProFTPD 1.3.4a', 'FileZilla ftp 0.9.43',
                               'Gene6 ftpd 3.10.0', 'FileZilla ftp 0.9.33', 'ProFTPD 1.2.8']
        self.process = None
        self.uuid = 'honeypotslogger'
        self.config = config
        if config:
            self.logs = setup_logger(self.uuid, config)
        else:
            self.logs = setup_logger(self.uuid, None)
        disable_logger(1, tlog)

    def ftp_server_main(self):
        _q_s = self

        class CustomFTPProtocol(FTP):

            def ftp_PASS(self, password):
                if self._user == _q_s.username and password == _q_s.password:
                    _q_s.logs.info({'server': 'ftp_server', 'action': 'login', 'status': 'success', 'ip': self.transport.getPeer(
                    ).host, 'port': self.transport.getPeer().port, 'username': _q_s.username, 'password': _q_s.password})
                else:
                    _q_s.logs.info({'server': 'ftp_server', 'action': 'login', 'status': 'failed', 'ip': self.transport.getPeer(
                    ).host, 'port': self.transport.getPeer().port, 'username': self._user, 'password': password})
                return AUTH_FAILURE

        class CustomFTPFactory(FTPFactory):
            protocol = CustomFTPProtocol
            portal = None

            def buildProtocol(self, address):
                p = self.protocol()
                p.portal = self.portal
                p.factory = self
                return p

        factory = CustomFTPFactory()
        reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
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
                        self.logs.info({'server': 'ftp_server', 'action': 'process', 'status': 'success',
                                        'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
                    else:
                        self.logs.info({'server': 'ftp_server', 'action': 'process', 'status': 'error',
                                        'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
                else:
                    self.logs.info({'server': 'ftp_server', 'action': 'setup', 'status': 'error', 'ip': self.ip,
                                    'port': self.port, 'username': self.username, 'password': self.password})
            elif self.close_port() and self.kill_server():
                self.process = Popen(['python3', path.realpath(__file__), '--custom', '--ip', str(self.ip), '--port', str(self.port), '--username', str(
                    self.username), '--password', str(self.password), '--mocking', str(self.mocking), '--config', str(self.config), '--uuid', str(self.uuid)])
                if self.process.poll() is None:
                    self.logs.info({'server': 'ftp_server', 'action': 'process', 'status': 'success',
                                    'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
                else:
                    self.logs.info({'server': 'ftp_server', 'action': 'process', 'status': 'error',
                                    'ip': self.ip, 'port': self.port, 'username': self.username, 'password': self.password})
        else:
            self.ftp_server_main()

    def close_port(self):
        ret = close_port_wrapper('ftp_server', self.ip, self.port, self.logs)
        return ret

    def kill_server(self):
        ret = kill_server_wrapper('ftp_server', self.uuid, self.process)
        return ret

    def test_server(self, ip=None, port=None, username=None, password=None):
        try:
            _ip = ip or self.ip
            _port = port or self.port
            _username = username or self.username
            _password = password or self.password
            f = FFTP()
            f.connect(_ip, _port)
            f.login(_username, _password)
        except BaseException:
            pass


if __name__ == '__main__':
    parsed = server_arguments()
    if parsed.docker or parsed.aws or parsed.custom:
        ftpserver = QFTPServer(ip=parsed.ip, port=parsed.port, username=parsed.username,
                               password=parsed.password, mocking=parsed.mocking, config=parsed.config)
        ftpserver.run_server()
