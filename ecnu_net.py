#! /usr/bin/python3
"""ecnu_net: ECNU Internet Login/Logout module"""

from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus
from urllib.error import URLError
import socket

from getpass import getpass
import os
import configparser

from argparse import ArgumentParser
from typing import Sequence


CONFIG_FILE_PATH = os.path.expanduser("~/.config/ECNU-net/config")
DNS_SERVER = '202.120.80.2' # ECNU dns server
TEST_URLS = ['http://ipv4.mirrors.ustc.edu.cn/',
             'http://www.tsinghua.edu.cn',
             'http://www.baidu.com',
             'https://www.sina.com.cn/',
             'https://www.qq.com/']

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

def internet_on(test_urls: Sequence[str] = None, pass_count=2):
    """
    check if internet is connected

    args
    - test_urls : list of urls for test
    - pass_count : if there're at least `pass_count` urls are connected,
        the test passes
    """
    if not test_urls:
        test_urls = TEST_URLS

    def _internet_on(url):
        try:
            urlopen(url, timeout=3)
            return True
        except (socket.timeout, URLError):
            return False

    on_count = 0
    for url in test_urls:
        on_count += _internet_on(url)
        if on_count == pass_count:
            return True  # return immediately
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

    def logout(self):
        """log out internet"""
        if not internet_on():
            print("Internet is already off, no ops.")
        else:
            # send exactly same package as login
            send_request(self._postdata)

            # the request result is useless, hence we
            # manually check internet connection
            if not internet_on():
                print("Success!")
            else:
                print("Failed! please re-check the username and password")
                if input("Continue? [y/N]") in ['y', 'Y', 'yes', 'YES']:
                    self.logout() # infinite recursion until success

    def login(self):
        """login internet"""
        if internet_on():
            print("Internet is already on, no ops.")
        else:
            send_request(self._postdata)

            # the request result is useless, hence we
            # manually check internet connection
            if internet_on():
                print("Success!")
            else:
                print("Failed! please re-check the username and password")
                if input("Continue? [y/N]") in ['y', 'Y', 'yes', 'YES']:
                    self.login()  # infinite recursion until success

    def _write_config(self, ask_write_password=True):
        config = configparser.ConfigParser()
        data = {'username': self._username}
        if ask_write_password:
            write_pass = input("write plain password? [y/N]") in ['y', 'Y', 'yes', 'YES']
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

    def _read_config(self, force_reread=False):
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

        self._username = input("Student ID: ") if read_username else config['username']
        password = getpass("Password: ") if read_password else config['password']
        again_password = getpass("Type again: ") if read_password else config['password']
        if password == again_password:
            self._password = password
        else:
            raise ValueError("Two passwords don't match, try again.")

        if write_config:
            self._write_config(ask_write_password)


def login():
    """login ECNU internet"""
    Loginer(POSTDATA_TEMPLATE).login()
def logout():
    """logout ECNU internet"""
    Loginer(POSTDATA_TEMPLATE).logout()
def update():
    """update configuration"""
    # update is done in initialization
    Loginer(POSTDATA_TEMPLATE, force_reread=True)


def main():
    """main function of module ecnu_net"""
    parser = ArgumentParser(description='ECNU internet login/logout script')
    group_parser = parser.add_mutually_exclusive_group()
    group_parser.add_argument('--login', action='store_true', help='internet login')
    group_parser.add_argument('--logout', action='store_true', help='internet login')
    group_parser.add_argument('--update', action='store_true', help='update configuration')
    args = parser.parse_args()

    if args.login:
        login()
        exit()
    if args.logout:
        logout()
        exit()
    if args.update:
        update()
        exit()

    parser.print_help()

if __name__ == '__main__':
    main()
