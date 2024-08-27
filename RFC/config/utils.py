import getpass
import socket


def get_username():
    return getpass.getuser()


def get_hostname():
    return socket.gethostname()