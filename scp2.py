import os
import paramiko

# Local directory path
local_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp'

# Remote server information
hostname = 'ec2-16-16-94-160.eu-north-1.compute.amazonaws.com'
username = 'ubuntu'
remote_path = '/home/ubuntu/FileSyncron/temp'
pem_key_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/ssh/dfs-services.pem'

# Connect to the remote server
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
pem_key = paramiko.RSAKey.from_private_key_file(pem_key_path)
ssh_client.connect(hostname, username=username, pkey=pem_key, look_for_keys=False, allow_agent=False)

# create SCP client and transfer directory
scp_client = ssh_client.open_sftp()
scp_client.put(local_path, remote_path, recursive=True)
scp_client.close()

# close SSH client
ssh_client.close()
