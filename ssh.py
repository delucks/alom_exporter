import time
from contextlib import suppress

import paramiko
import yaml


with open('config.yaml', 'r') as stream:
    config = yaml.safe_load(stream)
ilom_authentication_delay = 2
ilom_environment_delay = 2

client = paramiko.client.SSHClient()
#transport = paramiko.Transport((config['ilom_ssh_address'], 22))
#opts = transport.get_security_options()
#print(opts.kex)
#print(opts.key_types)
#print(opts.ciphers)
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Authentication happens with the "none" method
with suppress(paramiko.ssh_exception.AuthenticationException):
    client.connect(config['ilom_ssh_address'], username=config['ilom_ssh_username'], password=config['ilom_ssh_password'], look_for_keys=False)
client.get_transport().auth_none(config['ilom_ssh_username'])

channel = client.invoke_shell()

buf = b''
while not buf.startswith(b'Please login:'):
    buf = channel.recv(10000)
    print(buf.decode('utf-8'))

sent = channel.send(config['ilom_ssh_username']+'\n')
print(f'Sent {sent} bytes, sleeping {ilom_authentication_delay} seconds')
time.sleep(ilom_authentication_delay)
buf = channel.recv(10000)
trimmed = buf[sent+1:]

if not trimmed.startswith(b'Please Enter password:'):
    print(f'Authentication failed before sending password {buf}')

print(f'{buf}')
sent = channel.send(config['ilom_ssh_password']+'\n')
print(f'Sent {sent} bytes, sleeping {ilom_authentication_delay} seconds')
time.sleep(ilom_authentication_delay)
buf = channel.recv(10000)
buf = buf[sent+1:]
print(f'{buf}')
if b'sc> ' in buf:
    print('Authentication succeeded!')

sent = channel.send('showenvironment\n')
print(f'Sent {sent} bytes, sleeping for {ilom_environment_delay} seconds')
time.sleep(ilom_environment_delay)
buf = channel.recv(10000)
buf = buf[sent+1:]
print(f'{buf}')

client.close()
