
import socket, time
import pdb,os
import paramiko
import Pyro5.api
from paramiko import SSHClient
from scp import SCPClient

ip = socket.gethostbyname_ex(socket.gethostname())[-1]

dir_list = []
deleted_files = []
ip_add = '10.2.129.127'

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, look_for_keys=False, allow_agent=False)
    return client

def delete_file(deleted_files, s):
    if(len(deleted_files) > 0):
        del_msg = 'delete '

        for file in deleted_files:
            dir_list.remove(file)

        for file in deleted_files:
            del_msg += str(file) + ' '
        s.sendall(bytes(del_msg, 'UTF-8'))
    
def add_file(new_files, s):
    if(len(new_files) > 0):
        add_msg = 'add '

        for file in new_files:
            dir_list.append(file)

        for file in new_files:
            add_msg += str(file) + ' '
            ssh = createSSHClient(ip_add, '22', 'nilesh', '041997')
            scp = SCPClient(ssh.get_transport())
            scp.put('./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
            scp.close()
        s.sendall(bytes(add_msg, 'UTF-8'))

def dir_scanner(s):
    temp = os.listdir('./temp')
    new_files = [file for file in temp if file not in dir_list]
    deleted_files = [file for file in dir_list if file not in temp]
    # for i in new_files:
    #     dir_list.append(i)
    # if len(new_files)!=0:
    #     print(new_files)
    #     for file in new_files:
    #         ssh = createSSHClient(ip_add, '22', 'nilesh', '041997')
    #         scp = SCPClient(ssh.get_transport())
    #         scp.put('./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp', recursive=True)
    #         scp.close()
    add_file(new_files,s)
    delete_file(deleted_files, s)

def detect_deleted_file_from_master():
    master = Pyro5.api.Proxy('PYRO:file_syncron@' + ip_add + ':9002')
    # print(ip)
    msg = (master.check_deleted_file())
    if msg:

        print(msg)
        file_list = msg.split(' ')
        for file in file_list:
            file_path = './temp/' + file
            if file in list(dir_list):
                os.remove(file_path)
                dir_list.remove(file)
    
    master._pyroRelease()

def detect_new_files_from_master():
    master = Pyro5.api.Proxy('PYRO:file_syncron@' + ip_add + ':9002')
    msg = (master.check_added_file())
    # if msg != ' '.join(dir_list):
    #     print(msg)
    if msg:
        file_list = msg.split(' ')
        for file in file_list:
            if file not in dir_list:
                print(file)
                ssh = createSSHClient( ip_add, '22', 'nilesh', '041997')
                scp = SCPClient(ssh.get_transport())
                scp.get(local_path='./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                scp.close()
    master._pyroRelease()
    
    

# def Main1():
port = 8083
# pdb.set_trace()
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# connect to server on local computer
s.connect((ip_add,port))
s.sendall(bytes("vishal Vishal8199 " + os.getcwd() +"/temp",'UTF-8'))

ssh = createSSHClient( ip_add, '22', 'nilesh', '041997')
scp = SCPClient(ssh.get_transport())
scp.get(local_path='./', remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp', recursive=True)
scp.put('./temp', remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron', recursive=True)
scp.close()  
while True:
    dir_scanner(s)
    detect_deleted_file_from_master()
    detect_new_files_from_master()
s.close()

# Main1()