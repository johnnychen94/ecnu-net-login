#!/usr/bin/env python3

description = """
ECNU internet login/logout script

Copyright (C) 2019 Jiuning Chen <johnnychen94@hotmail.com>

Distributed under terms of the MIT license.

This script is hosted at both LAN and WAN network:

* Github: https://github.com/johnnychen94/ecnu-net-login
* Gitlab@LFLab.ECNU: https://gitlab.lflab.cn/lflab/ecnu-net-login
"""

from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus
from urllib.error import URLError
import socket

from getpass import getpass
import time
from datetime import datetime
import os
import configparser

from argparse import ArgumentParser

import math
from random import shuffle


CONFIG_FILE_PATH = os.path.expanduser("~/.config/ecnu_net/config")
DNS_SERVER = '202.120.80.2' # ECNU dns server

# Only when ipv4 network is connected can we connect urls in this list
TEST_URLS = ['https://www.baidu.com/',
             'https://www.taobao.com/',
             'https://www.amazon.cn/',
             'https://www.jd.com/',
             'https://www.bing.com',
             'http://www.cnki.net/',
             'https://www.qq.com/',
             'https://www.csdn.net/',
             'https://gitee.com/',
             'https://www.zhihu.com/',
             'https://www.aliyun.com/',
             'https://arxiv.org/']

AC_ID = '4'
LOGIN_URL = 'http://gateway.ecnu.edu.cn/srun_portal_pc.php?ac_id=' + str(AC_ID)

POSTDATA_TEMPLATE = {
    'username': '',
    'password': '',
    'action': 'login',
    'ac_id': AC_ID,
    'user_ip': '',
    'nas_ip': '',
    'user_mac': '',
    'url': ''
}

def send_request(postdata: dict):
    """send request filled with postdata"""
    postdata = urlencode(postdata, quote_via=quote_plus).encode("utf-8")
    action_request = Request(url=LOGIN_URL, data=postdata)
    return urlopen(action_request).read()

def internet_on(test_urls= None, pass_ratio=0.6, timeout=1, verbose=True):
    """
    check if internet is connected

    args
    - test_urls : list of urls for test
    - pass_count : if there're at least `pass_count` urls are connected,
        the test passes
    """
    if not test_urls:
        test_urls = TEST_URLS
    test_urls = test_urls.copy()
    shuffle(test_urls)

    def _internet_on(url, timeout):
        try:
            urlopen(url, timeout=timeout)
            return True
        except (socket.timeout, URLError, ConnectionResetError):
            return False

    on_count = 0
    off_count = 0
    pass_count = math.floor(pass_ratio * len(test_urls))
    fail_count = len(test_urls) - pass_count

    def _get_test_urls(test_urls, verbose):
        return test_urls

    if verbose:
        print("check internet connection...")

    for url in _get_test_urls(test_urls, verbose):
        rst = _internet_on(url, timeout)
        on_count += rst
        off_count += 1-rst
        if on_count == pass_count:
            return True  # return immediately
        if off_count == fail_count:
            return False

def get_ip(dns=DNS_SERVER):
    """get the current ip address"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as tmp_socket:
        tmp_socket.connect((dns, 80))
        ip_address = tmp_socket.getsockname()[0]
    return ip_address

class Loginer():
    """ECNU network login class"""
    def __init__(self, postdata, force_reread=False):
        """
        initialize Loginer instance

        args
        - force_reread : True to update/force_reread the config

        methods:
        - logout : logout internet
        - login : login internet
        """
        self._read_config(force_reread)
        self._postdata = postdata.copy()
        self._postdata['username'] = self._username
        self._postdata['password'] = self._password
        self._postdata['user_ip'] = get_ip(DNS_SERVER)

    def logout(self, verbose=True, prompt=True):
        """log out internet"""
        if not internet_on(verbose=verbose):
            print("Internet is already off, no ops.")
        else:
            # send exactly same package as login
            print("Logout...")
            send_request(self._postdata)

            # the request result is useless, hence we
            # manually check internet connection
            if not internet_on(verbose=verbose):
                print("Success!")
            elif prompt:
                if input("Failed! Retry? [Y/n]") not in ['n', 'N', 'no', 'NO']:
                    # infinite recursion until success
                    self.logout(verbose=verbose)
                else:
                    print("Failed!")

    def login(self, verbose=True, prompt=True):
        """login internet"""
        if internet_on(verbose=verbose):
            print("Internet is already on, no ops.")
        else:
            print("Login...")
            send_request(self._postdata)

            # the request result is useless, hence we
            # manually check internet connection
            if internet_on(verbose=verbose):
               print("Success!")
            elif prompt:
                if input("Failed! Retry? [Y/n]") not in ['n', 'N', 'no', 'NO']: 
                    # infinite recursion until success
                    self.login(verbose=verbose)
                else:
                    print("Failed!")

    def _write_config(self, ask_write_password=True):
        config = configparser.ConfigParser()
        data = {'username': self._username}
        if ask_write_password:
            write_pass = input("write plain password? [y/N]") in ['y', 'Y', 'yes', 'YES']
            confirm = input("This can be risky if others have access to your data, are you sure?") in ['y', 'Y', 'yes', 'YES']
            write_pass = write_pass and confirm
        else:
            write_pass = False
        if write_pass:
            print("Store plain password, Make sure nobody sees your password.")
            data['password'] = self._password

        config['user'] = data

        root_dir = os.path.split(CONFIG_FILE_PATH)[0]
        if not os.path.isdir(root_dir):
            os.makedirs(os.path.split(CONFIG_FILE_PATH)[0])
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)

    def _read_config(self, force_reread=False, write_config=False):
        config = configparser.ConfigParser()
        has_config_file = config.read(CONFIG_FILE_PATH)
        if has_config_file:
            config = config['user']
        else:
            config = None

        write_config = False

        if config and (not force_reread):
            read_username = 'username' not in config.keys()
            read_password = 'password' not in config.keys()
            ask_write_password = False
        else:
            read_username = True
            read_password = True
            ask_write_password = True

        write_username = read_username
        write_password = read_password
        write_config = write_username or write_password

        # read config from stdin
        self._username = input("Student ID: ") if read_username else config['username']
        password = getpass("Password: ") if read_password else config['password']
        again_password = getpass("Type again: ") if read_password else config['password']
        if password == again_password:
            self._password = password
        else:
            raise ValueError("Two passwords don't match, try again.")

        if write_config:
            self._write_config(ask_write_password)


def login(**kwargs):
    """login ECNU internet"""
    Loginer(POSTDATA_TEMPLATE).login(**kwargs)
def logout(**kwargs):
    """logout ECNU internet"""
    Loginer(POSTDATA_TEMPLATE).logout(**kwargs)
def update():
    """update configuration"""
    # update is done in initialization
    Loginer(POSTDATA_TEMPLATE, force_reread=True)


def main():
    """main function of module ecnu_net"""
    parser = ArgumentParser(description=description)
    group_parser = parser.add_mutually_exclusive_group()
    group_parser.add_argument('--login', action='store_true', help='internet login')
    group_parser.add_argument('--logout', action='store_true', help='internet login')
    group_parser.add_argument('--update', action='store_true', help='update configuration')
    parser.add_argument('--verbose', action='store_true', help='show detail information')
    parser.add_argument('--daemon', action='store_true', help='login/logout as a daemon service')

    args = parser.parse_args()

    if args.daemon:
        while True:
            print(datetime.now().ctime())
            Loginer(POSTDATA_TEMPLATE, force_reread=False)
            if args.update:
                raise ValueError("update doesn't support daemon mode.")
            if args.login:
                login(verbose=args.verbose, prompt=False)
            if args.logout:
                logout(verbose=args.verbose, prompt=False)
            time.sleep(120)
    
    if args.login:
        login(verbose=args.verbose)
        exit()
    if args.logout:
        logout(verbose=args.verbose)
        exit()
    if args.update:
        update()
        exit()

    parser.print_help()

if __name__ == '__main__':
    main()
