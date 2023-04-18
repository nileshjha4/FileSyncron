import paramiko
from scp import SCPClient

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, look_for_keys=False, allow_agent=False)
    return client

ssh = createSSHClient( '10.2.133.88','22', 'purnima', 'Ketan1411')
scp = SCPClient(ssh.get_transport())
scp.put('./temp', remote_path = '/home/purnima/Downloads', recursive=True)
scp.close()