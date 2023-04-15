
# import paramiko
# from scp import SCPClient

# def createSSHClient(server, port, user, password):
#     client = paramiko.SSHClient()
#     client.load_system_host_keys()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     client.connect(server, port, user, password, look_for_keys=False, allow_agent=False)
#     return client

# print("Enter IP address of the server")
# ip_addr = input()
# ssh = createSSHClient( ip, port, username, password)
# scp = SCPClient(ssh.get_transport())
# scp.put('LICENSE', './LICENSE')
# scp.close()

# import socket
# SERVER = "10.2.133.164"
# PORT = 8081
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect((SERVER, PORT))
# client.sendall(bytes("This is from Client-check",'UTF-8'))
# while True:
  
#   out_data = input()
#   client.sendall(bytes(out_data,'UTF-8'))
#   in_data =  client.recv(1024)
#   print("From Server :" ,in_data.decode())
#   if out_data=='bye':
#     break
# client.close()
import socket
import pdb,os
import paramiko

from paramiko import SSHClient
from scp import SCPClient

dir_list = []

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, look_for_keys=False, allow_agent=False)
    return client

def dir_scanner():
	temp = os.listdir('./temp')
	new_files = [file for file in temp if file not in dir_list]
	for i in new_files:
		dir_list.append(i)
	if len(new_files)!=0:
		print(new_files)
		for file in new_files:
			ssh = createSSHClient('10.2.133.164','22', 'nilesh', '041997')
			scp = SCPClient(ssh.get_transport())
			scp.put('./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp', recursive=True)
			scp.close()

def Main1():
    # local host IP '127.0.0.1'
    # pdb.set_trace()
    
    host = '10.2.133.164'
    port = 8083

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # connect to server on local computer
    s.connect((host,port))
    s.sendall(bytes("purnima Ketan1411 " + os.getcwd() +"/temp",'UTF-8'))

    ssh = createSSHClient( '10.2.133.164','22', 'nilesh', '041997')
    scp = SCPClient(ssh.get_transport())
    scp.get(local_path='./', remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp', recursive=True)
    scp.put('./temp', remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron', recursive=True)
    scp.close()  
    while True:
        dir_scanner()   
    s.close()

Main1()