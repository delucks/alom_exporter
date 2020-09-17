import logging
import time
from contextlib import suppress

import paramiko
import yaml

log = logging.getLogger(__name__)


class ILOMConnection:
    '''ILOMConnection wraps a paramiko.client to authenticate with Sun Integrated Lights-Out Management via SSH.
    The class is used as a context manager to properly tear down the SSH connection.
    Initial authentication takes some time (~5s) but subsequent calls are relatively quick.
    '''
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as stream:
            config = yaml.safe_load(stream)
        if not 'ilom_authentication_delay' in config:
            config['ilom_authentication_delay'] = 2
        if not 'ilom_environment_delay' in config:
            config['ilom_environment_delay'] = 2
        self.config = config
        self.client = None
        self.channel = None

    def __enter__(self):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Authentication happens with the "none" method, which is not officially supported.
        # https://github.com/paramiko/paramiko/issues/890
        with suppress(paramiko.ssh_exception.AuthenticationException):
            client.connect(
                self.config['ilom_ssh_address'],
                username=self.config['ilom_ssh_username'],
                password=self.config['ilom_ssh_password'],
                look_for_keys=False
            )
        client.get_transport().auth_none(self.config['ilom_ssh_username'])
        self.client = client
        self.channel = client.invoke_shell()

        if self.authenticate():
            return self
        else:
            self.client.close()
            raise Exception('ILOM authentication failed')

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def authenticate(self) -> bool:
        delay = self.config['ilom_authentication_delay']
        buf = b''
        while not buf.startswith(b'Please login:'):
            buf = self.channel.recv(10000)
            log.debug(buf.decode('utf-8'))
        sent = self.channel.send(self.config['ilom_ssh_username']+'\n')
        log.info(f'Sent {sent} bytes, sleeping {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        trimmed = buf[sent+1:]

        if not trimmed.startswith(b'Please Enter password:'):
            log.warning(f'Authentication failed before sending password {buf}')
            return False

        log.debug(f'{buf}')
        sent = self.channel.send(self.config['ilom_ssh_password']+'\n')
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
        delay = self.config['ilom_environment_delay']
        sent = self.channel.send('showenvironment\n')
        log.info(f'Sent {sent} bytes, sleeping for {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        buf = buf[sent+1:]
        log.debug(f'{buf}')
        return buf.decode('utf-8')

if __name__ == '__main__':
    with ILOMConnection() as connection:
        print(connection.showenvironment())
