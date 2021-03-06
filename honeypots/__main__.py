#!/usr/bin/env python

from json import JSONEncoder, dumps, load
from uuid import uuid4
from psutil import Process, net_io_counters
from netifaces import ifaddresses, AF_INET, AF_LINK
from subprocess import Popen
from sys import stdout
from argparse import ArgumentParser
from atexit import register
from time import sleep
from honeypots import QDNSServer, QFTPServer, QHTTPProxyServer, QHTTPServer, QHTTPSServer, QIMAPServer, QMysqlServer, QPOP3Server, QPostgresServer, QRedisServer, QSMBServer, QSMTPServer, QSOCKS5Server, QSSHServer, QTelnetServer, QVNCServer, server_arguments, clean_all, postgres_class, setup_logger, QBSniffer, get_running_servers
from warnings import filterwarnings
filterwarnings(action='ignore', module='.*OpenSSL.*')


all_servers = ['QDNSServer', 'QFTPServer', 'QHTTPProxyServer', 'QHTTPServer', 'QHTTPSServer', 'QIMAPServer', 'QMysqlServer', 'QPOP3Server',
               'QPostgresServer', 'QRedisServer', 'QSMBServer', 'QSMTPServer', 'QSOCKS5Server', 'QSSHServer', 'QTelnetServer', 'QVNCServer']

temp_honeypots = []


def exit_handler():
    print("Cleaning")
    clean_all()
    sleep(1)


def list_all_honeypots():
    for honeypot in all_servers:
        print(honeypot[1:].replace('Server', '').lower())


def msg():
    '''
    welcome message
    '''
    return """\npython3 -m honeypots --setup all\npython3 -m honeypots --setup ssh --logs all --logs_location /tmp/honeypots_logs\n"""


ARG_PARSER = ArgumentParser(
    description="Qeeqbox/honeypots customizable honeypots for monitoring network traffic, bots activities, and username\\password credentials", usage=msg())
ARG_PARSER.add_argument(
    "--setup", help="target honeypot E.g. ssh or you can have multiple E.g ssh,http,https", metavar="", default="")
ARG_PARSER.add_argument("--list", action="store_true",
                        help="list all available honeypots")
ARG_PARSER.add_argument("--kill", action="store_true",
                        help="kill all honeypots")
ARG_PARSER.add_argument("--chameleon", action="store_true",
                        help="reserved for chameleon project")
ARG_PARSER.add_argument(
    "--config", help="config file for logs and database", metavar="", default="")
ARGV = ARG_PARSER.parse_args()

if __name__ == "__main__":
    if ARGV.list:
        list_all_honeypots()
    elif ARGV.kill:
        clean_all()
    elif ARGV.chameleon and ARGV.config and ARGV.config != '':
        port = None
        interface = None
        honeypots = None
        with open(ARGV.config) as f:
            config_data = load(f)
            port = config_data['port']
            interface = config_data['interface']
            honeypots = config_data['honeypots']
        if port and interface:
            print('Your IP: {}'.format(
                ifaddresses(interface)[AF_INET][0]['addr']))
            print('Your MAC: {}'.format(
                ifaddresses(interface)[AF_LINK][0]['addr']))
            Popen(
                'iptables -A OUTPUT -p tcp -m tcp --tcp-flags RST RST -j DROP', shell=True)
            print('Wait for 10 seconds..')
            stdout.flush()
            sleep(2)
            uuid = 'honeypotslogger'
            logs = setup_logger(uuid, ARGV.config, True)
            servers = []
            if honeypots:
                for server in honeypots.split(','):
                    if ":" in server:
                        for honeypot in all_servers:
                            if 'q{}server'.format(server.split(':')[0]).lower() == honeypot.lower():
                                x = globals()[honeypot](
                                    port=int(server.split(':')[1]), config=ARGV.config)
                                x.run_server(process=True)
                                temp_honeypots.append(x)
                    else:
                        for honeypot in all_servers:
                            if 'q{}server'.format(server).lower() == honeypot.lower():
                                x = globals()[honeypot](config=ARGV.config)
                                x.run_server(process=True)
                                temp_honeypots.append(x)
            else:
                for honeypot in all_servers:
                    x = globals()[honeypot](config=ARGV.config)
                    x.run_server(process=True)
                    temp_honeypots.append(x)

            x = globals()['QBSniffer'](filter='not port {}'.format(
                port), interface=interface, config=ARGV.config)
            x.run_sniffer(process=True)
            temp_honeypots.append(x)
            while True:
                try:
                    _servers = {}
                    logs.info({'type': 'network', 'bytes_sent': net_io_counters().bytes_sent, 'bytes_recv': net_io_counters(
                    ).bytes_recv, 'packets_sent': net_io_counters().packets_sent, 'packets_recv': net_io_counters().packets_recv})
                    for server in temp_honeypots:
                        _servers[server.__class__.__name__] = {'memory': Process(
                            server.process.pid).memory_percent(), 'cpu': Process(server.process.pid).cpu_percent()}
                    logs.info(['system', _servers])
                except Exception as e:
                    pass
                sleep(20)
    elif ARGV.setup != "":
        print("Use [Enter] to exit or python3 -m honeypots --kill")
        register(exit_handler)
        if ARGV.setup == "all":
            for honeypot in all_servers:
                x = globals()[honeypot](config=ARGV.config)
                x.run_server(process=True, auto=True)
                temp_honeypots.append(x)
        else:
            servers = ARGV.setup.split(',')
            for server in servers:
                if ":" in server:
                    for honeypot in all_servers:
                        if 'q{}server'.format(server.split(':')[0]).lower() == honeypot.lower():
                            x = globals()[honeypot](
                                port=int(server.split(':')[1]), config=ARGV.config)
                            x.run_server(process=True)
                            temp_honeypots.append(x)
                else:
                    for honeypot in all_servers:
                        if 'q{}server'.format(server).lower() == honeypot.lower():
                            x = globals()[honeypot](config=ARGV.config)
                            x.run_server(process=True, auto=True)
                            temp_honeypots.append(x)
        if len(temp_honeypots) > 0:
            input("")
            for server in temp_honeypots:
                try:
                    print("Killing {}".format(server.__class__.__name__))
                    server.kill_server()
                except BaseException:
                    pass
            print("Please wait few seconds")
            sleep(5)
