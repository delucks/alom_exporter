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
            # Range 0.35 for a powered off system to 3.0 for a powered on system
            config['alom_environment_delay'] = 3.00
        self.config = config
        self.client = None
        self.channel = None
        self.last_measurement_on = True

    def _get_delay(self):
        if self.last_measurement_on:
            return self.config['alom_environment_delay']
        else:
            return 0.35

    def __enter__(self):
        for required_property in ['alom_ssh_address', 'alom_ssh_username', 'alom_ssh_password']:
            if not required_property in self.config:
                raise Exception('Property {required_property} not found in configuration file')
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        log.debug(f'Connecting to {self.config["alom_ssh_address"]} over SSH')
        # Authentication happens with the "none" method, which is not officially supported.
        # https://github.com/paramiko/paramiko/issues/890
        with suppress(paramiko.ssh_exception.AuthenticationException):
            client.connect(
                self.config['alom_ssh_address'],
                username=self.config['alom_ssh_username'],
                password=self.config['alom_ssh_password'],
                look_for_keys=False
            )
        log.debug(f'Authenticating as {self.config["alom_ssh_username"]}')
        client.get_transport().auth_none(self.config['alom_ssh_username'])
        self.client = client
        log.debug('Requesting pty')
        self.channel = client.invoke_shell()

        if self.authenticate():
            log.debug('Connection successful')
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
        delay = self._get_delay()
        sent = self.channel.send('showenvironment\n')
        log.info(f'Sent {sent} bytes, sleeping for {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(40000)
        buf = buf[sent+1:]
        from_the_binary = buf.decode('utf-8')
        log.debug(from_the_binary)
        # Adjust next recv delay based on power-off status
        self.last_measurement_on = 'power is off' not in from_the_binary
        return from_the_binary
