import logging
import time
from contextlib import suppress

import paramiko
import yaml

log = logging.getLogger(__name__)


class ALOMConnection:
    '''ALOMConnection wraps a paramiko.client to authenticate with Sun Integrated Lights-Out Management via SSH.
    The class is used as a context manager to properly tear down the SSH connection.
    Initial authentication takes some time (~5s) but subsequent calls are relatively quick.
    '''
    def __init__(self, config_path):
        with open(config_path, 'r') as stream:
            config = yaml.safe_load(stream)
        if not 'alom_authentication_delay' in config:
            config['alom_authentication_delay'] = 2
        if not 'alom_environment_delay' in config:
            # This is the lowest value which seems to consistently work
            config['alom_environment_delay'] = 0.35
        self.config = config
        self.client = None
        self.channel = None

    def __enter__(self):
        for required_property in ['alom_ssh_address', 'alom_ssh_username', 'alom_ssh_password']:
            if not required_property in self.config:
                raise Exception('Property {required_property} not found in configuration file')
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Authentication happens with the "none" method, which is not officially supported.
        # https://github.com/paramiko/paramiko/issues/890
        with suppress(paramiko.ssh_exception.AuthenticationException):
            client.connect(
                self.config['alom_ssh_address'],
                username=self.config['alom_ssh_username'],
                password=self.config['alom_ssh_password'],
                look_for_keys=False
            )
        client.get_transport().auth_none(self.config['alom_ssh_username'])
        self.client = client
        self.channel = client.invoke_shell()

        if self.authenticate():
            return self
        else:
            self.client.close()
            raise Exception('ALOM authentication failed')

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def authenticate(self) -> bool:
        delay = self.config['alom_authentication_delay']
        buf = b''
        while not buf.startswith(b'Please login:'):
            buf = self.channel.recv(10000)
            log.debug(buf.decode('utf-8'))
        sent = self.channel.send(self.config['alom_ssh_username']+'\n')
        log.info(f'Sent {sent} bytes, sleeping {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        trimmed = buf[sent+1:]

        if not trimmed.startswith(b'Please Enter password:'):
            log.warning(f'Authentication failed before sending password {buf}')
            return False

        log.debug(f'{buf}')
        sent = self.channel.send(self.config['alom_ssh_password']+'\n')
        log.info(f'Sent {sent} bytes, sleeping {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        buf = buf[sent+1:]
        log.debug(f'{buf}')

        if b'sc> ' in buf:
            log.info('Authentication succeeded!')
            return True
        return False

    def showenvironment(self) -> str:
        delay = self.config['alom_environment_delay']
        sent = self.channel.send('showenvironment\n')
        log.info(f'Sent {sent} bytes, sleeping for {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        buf = buf[sent+1:]
        log.debug(f'{buf}')
        return buf.decode('utf-8')
