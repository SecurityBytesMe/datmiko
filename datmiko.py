#!/usr/bin/env python

"""
Datmiko (DevOps Automation Tool Miko) leverages netmiko
and multiprocessing to bring you parallelism to your network configurations.
"""

import getpass
import re
import signal
import sys
import textwrap

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from multiprocessing import Pool
from netmiko import ConnectHandler, NetMikoTimeoutException, NetmikoAuthError

# TODO: add argument for CLI and File of command to run on switches

parser = ArgumentParser(
         description='datmiko.py runs commands on switches very fast '
                     'Please use with care',
         formatter_class=RawDescriptionHelpFormatter,
         epilog=textwrap.dedent('''
         ---------------------------------
         Defaults:
                device_type = arista_eos
                port = 22
                command = show version'''))
parser.add_argument('-d', '--device_type', dest='device_type',
                    type=str, help='arista_eos, cisco_ios, junos')
parser.add_argument('-u', '--username', dest='username', required=True,
                    type=str, help="provide username for switch.")
parser.add_argument('-p', '--password', dest='password',
                    type=str, help="provide password for switch.")
parser.add_argument('-s', '--switches', dest='switches', nargs='+',
                    help="Switches you want to run commands on. " +
                         "Only supply a space between each")
parser.add_argument('-f', '--filename', dest='filename',
                    type=str, help="filename with switches in single column")
args = parser.parse_args()


# commands = ['ip domain-name example.com',
#             'ip name-server IPADDRESS',
#             'ip name-server IPADDRESS',
#             'no ntp server IPADDRESS',
#             'no ntp server IPADDRESS',
#             'ntp server example-clock.com prefer',
#             'ntp server c14-ipv6clock.examplecom',
#             'write memory']

commands = ['show version']


def main():
    global switches

    switches = args.switches
    filename = args.filename

    if args.password is None:
        args.password = getpass.getpass(prompt=" Password: ")

    if filename:
        try:
            with open(filename, 'r') as f:
                switches = f.read().splitlines()
        except IOError as e:
            print(e)
            print "Check file name and/or path"
            sys.exit(1)

    if switches is None:
        switches = raw_input("Enter switches (seperated by , and space" +
                             "ex: a , b , c): ").replace(' ', '').split(',')

    do_check(switches)


def do_netmiko(switches, commands=commands):
    """Iterates commands over a list of switches
   commands='command 1'
   commands=['command 1', 'command 2']
   This can be a list or a string"""
    device = {
        'device_type': 'arista_eos',
        'ip': switches,
        'username': args.username,
        'password': args.password,
        'port': 22,
    }
    net_connect = ConnectHandler(**device)

    # Checking prompt for "admin" since 'fc' can be either Brocade or Cisco
    # Return here if we find naming scheme for FC.
    # You may not need this
    if re.findall(device['username'], net_connect.find_prompt()):
        return

    net_connect.enable()
    output = net_connect.send_config_set(commands)
    rc = net_connect.check_enable_mode()  # Works for Arista and Cisco
    ip = net_connect.ip
    net_connect.disconnect()
    return {'output': output, 'rc': rc, 'ip': ip}


def parallel_check(hosts):
    """
    Takes the sshcmd object created and checks for the return codes
    """

    try:
        result = do_netmiko(hosts, commands)
        # Catch any netmiko objects that return as None (for whatever reason)
        if result is None:
            return None
    except NetMikoTimeoutException:
        return None
    except NetmikoAuthError:
        return None
    # print result ## turn this on to see dict
    if result['rc']:
        _title(hosts)
        print result['output']
    if not result['rc']:
        return None
    else:
        return hosts


def poolrunner(func, hosts):
    """
    returns pool.map(func, hosts) will be used in do_check
    with paralellel_check and hosts which is passed
    to do_check as a list of hosts
    """
    # if we don't have at least 1 host, don't bother
    if len(hosts) < 1:
        return None

    threads = max(min(100, len(hosts)), 2)
    pool = Pool(threads, init_worker)

    try:
        results = pool.map(func, hosts)
    except KeyboardInterrupt:
        print
        _error('Caught CTRL-C, bailing')
        pool.terminate()
        pool.join()
        sys.exit(-1)
    except Exception as e:
        _error("Unable to run Pool: %s" % e)
    else:
        pool.close()
        pool.join()
        return results


def init_worker():
    """
    initializes each worker individually SIG_IN keeps connection open
    signal(sig, action) -> action
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def do_check(hosts):
    """
    Where the magic happens. poolrunner takes parallel_check
    and hosts as arguments here and displays the results
    """

    _info('Running commands on switches')
    print
    results = poolrunner(parallel_check, hosts)
    label = 'able to get switch info!'
    good = sorted([r for r in results if r])
    if len(good):
        if len(good) == len(hosts):
            _ok("All %s hosts %s" % (len(hosts), label))
            print results
            print
        else:
            _warn("only %s/%s switches %s:" % (
                len(good), len(hosts), label))
            print "\n".join(good)
            bad = set(switches) - set(results)
            _warn("%s/%s switches unable to connect" % (
                len(bad), len(hosts)))
            for bad_switches in bad:
                print bad_switches
    if len(good) == 0:
        _error("No host %s!" % label)


# Formatters
def _title(msg):
    brwhite = "\033[1;97m{0}\033[00m"
    print
    print brwhite.format("%s switch results" % msg)


def _info(msg):
    print "* %s" % msg


def _ok(msg):
    green = "\033[1;32m{0}\033[00m"
    print green.format("+ %s" % msg)


def _warn(msg):
    yellow = "\033[01;33m{0}\033[00m"
    print yellow.format("- %s" % msg)


def _error(msg):
    red = "\033[01;31m{0}\033[00m"
    print red.format("- %s" % msg)


if __name__ == '__main__':
    main()
