import logging
import time
from contextlib import suppress

import paramiko
import yaml

log = logging.getLogger(__name__)


class ALOMConnection:
    """ALOMConnection wraps a paramiko.client to authenticate with Sun Integrated Lights-Out Management via SSH.
    The class is used as a context manager to properly tear down the SSH connection.
    Initial authentication takes some time (~5s) but subsequent calls are relatively quick.
    """

    def __init__(self, config_path):
        with open(config_path, 'r') as stream:
            config = yaml.safe_load(stream)
        # Establish delay times. These are necessary because the ALOM processor generally
        # runs slower than this daemon, and sending too much data at once causes it to get overwhelmed.
        # Authentication delay doesn't need much configuration; 2s seems to work in most cases.
        if not 'alom_authentication_delay' in config:
            config['alom_authentication_delay'] = 2
        # The delay before parsing "showenvironment" output, however, varies greatly depending
        # on system state. 350ms works for a powered-off system, but a powered on system
        # needs more like 3s- we use a backoff between these two values unless we know the
        # system power state.
        if not 'max_environment_delay' in config:
            config['max_environment_delay'] = 3.00
        if not 'min_environment_delay' in config:
            config['min_environment_delay'] = 0.35
        # if we know the system is powered on, we need to swap to the maximum wait time
        self.last_measurement_on = False
        # Backoff configuration for the above environment delay. By default, start with the minimum
        # delay and double each time increase the backoff.
        self.backoff = config['min_environment_delay']
        self.backoff_scaling_factor = 2.0
        self.config = config
        self.client = None
        self.channel = None

    def increase_backoff(self):
        new_wait = self.backoff * self.backoff_scaling_factor
        proper_wait = min(new_wait, self.config['max_environment_delay'])
        self.backoff = proper_wait
        return proper_wait

    def get_backoff(self):
        return self.config['max_environment_delay'] if self.last_measurement_on else self.backoff

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
                look_for_keys=False,
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
        log.info(f'Using {delay}s authentication delay')
        buf = b''
        while not buf.startswith(b'Please login:'):
            buf = self.channel.recv(10000)
            log.debug(buf.decode('utf-8'))
        sent = self.channel.send(self.config['alom_ssh_username'] + '\n')
        log.debug(f'Sent {sent} bytes, sleeping {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        trimmed = buf[sent + 1 :]

        if not trimmed.startswith(b'Please Enter password:'):
            log.warning(f'Authentication failed before sending password {buf}')
            return False

        log.debug(f'{buf}')
        sent = self.channel.send(self.config['alom_ssh_password'] + '\n')
        log.debug(f'Sent {sent} bytes, sleeping {delay} seconds')
        time.sleep(delay)
        buf = self.channel.recv(10000)
        buf = buf[sent + 1 :]
        log.debug(f'{buf}')

        if b'sc> ' in buf:
            log.info('Authentication succeeded!')
            return True
        log.warning(f'Authentication failed after sending password: {buf}')
        return False

    def showenvironment(self) -> str:
        backoff = self.get_backoff()
        sent = self.channel.send('showenvironment\n')
        log.info(f'Environment request waiting for {backoff}s')
        time.sleep(backoff)
        buf = self.channel.recv(40000)
        buf = buf[sent + 1 :]
        from_the_binary = buf.decode('utf-8')
        log.debug(from_the_binary)
        # Flag any changes in power status so the backoff can be changed
        power_is_on = 'power is off' not in from_the_binary
        if not power_is_on and power_is_on != self.last_measurement_on:
            # Power was just turned off! Reset the backoff logic with the minimum wait
            self.backoff = self.config['min_environment_delay']
        self.last_measurement_on = power_is_on
        return from_the_binary
