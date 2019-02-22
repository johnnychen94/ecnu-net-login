#! /usr/bin/python3 
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus
from urllib.error import URLError
import socket
from getpass import getpass
import os
import configparser
from argparse import ArgumentParser


CONFIG_FILE_PATH = os.path.expanduser("~/.config/ECNU-net/config")


class Loginer():
    def __init__(self):
        self._read_config()
        self._ac_id = 4
        self._loginUrl = 'http://gateway.ecnu.edu.cn/srun_portal_pc.php?ac_id=' + str(self._ac_id)
        
        
    def logout(self):
        if not self._internet_on():
            print("Internet is already off, no ops.")
        else:
            # send exactly same package as login
            postdata = {
                'username': self._username,
                'password': self._password,
                'action': 'login',
                'ac_id': self._ac_id,
                'user_ip': self.ip,
                'nas_ip':'',
                'user_mac':'',
                'url':''
            }
            self._send_request(postdata)

            # the request result is useless, hence we
            # manually check internet connection
            if not self._internet_on():
                print("Success!")
            else:
                print("Failed! please re-check the username and password")
                self._read_config(force_reread=True)
                self.logout() # infinite recursion until success
                
    def login(self):
        if self._internet_on():
            print("Internet is already on, no ops.")
        else:
            postdata = {
                'username': self._username,
                'password': self._password,
                'action': 'login',
                'ac_id': self._ac_id,
                'user_ip': self.ip,
                'nas_ip':'',
                'user_mac':'',
                'url':''
            }
            self._send_request(postdata)

            # the request result is useless, hence we
            # manually check internet connection
            if self._internet_on():
                print("Success!")
            else:
                print("Failed! please re-check the username and password")
                self._read_config(force_reread=True)
                self.login() # infinite recursion until success
                
    
    def _send_request(self, postdata):
        postdata = urlencode(postdata, quote_via=quote_plus).encode("utf-8")
        myRequest = Request(url=self._loginUrl, data=postdata)
        return urlopen(myRequest).read()
    
    def _write_config(self, ask_write_password=True):
        config = configparser.ConfigParser()
        data = {'username': self._username}
        if ask_write_password:
            write_pass = input("write plain password? [y/N]") in ['y','Y','yes','YES']
        else:
            write_pass = False
        if write_pass:
            print("Store plain password, Make sure nobody sees your password.")
            data['password'] = self._password
            
        config['user'] = data
        with open(CONFIG_FILE_PATH, 'w') as f:
            config.write(f)
    
    def _read_config(self, force_reread=False):
        config = configparser.ConfigParser()
        rst = config.read(CONFIG_FILE_PATH)
        config = None if len(rst)==0 else config['user']
    
        write_config = False
        
        if config and not force_reread:
            read_username = not 'username' in config.keys()
            read_password = not 'password' in config.keys()
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
        again_password = getpass("Password: ") if read_password else config['password']
        if password == again_password:
            self._password = password
        else:
            raise ValueError("Two passwords don't match, try again.")
        
        if write_config:
            self._write_config(ask_write_password)
    
    def _internet_on(self):
        try:
            urlopen('http://www.baiud.com', timeout=1)
            return True
        except socket.timeout as err: 
            return False
    
    @property
    def ip(self, dns='202.120.80.2'):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((dns, 80))
            ip = s.getsockname()[0]
        return ip


def login():
    Loginer().login()
def logout():
    Loginer().logout()


if __name__=='__main__':
    parser = ArgumentParser(description='ECNU internet login/logout script')
    parser.add_argument('--login', action='store_true', help='internet login')
    parser.add_argument('--logout', action='store_true', help='internet login')
    args = parser.parse_args()

    assert not(args.login == True == args.logout), "login or logout, not both."
    if args.login:
        login()
        exit()
    if args.logout:
        logout()
        exit()

    parser.print_help()
    

