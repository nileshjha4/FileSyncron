import socket, time
import pdb,os
import paramiko, sys
import Pyro5.api
from paramiko import SSHClient
from scp import SCPClient
import time
import hashed

ip = socket.gethostbyname_ex(socket.gethostname())[-1]
current_hashes={}
dir_list = []
ip_add = '10.2.129.127'
# modified_files = []

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
        # time.sleep(4)
    
def add_file(new_files, s):
    if(len(new_files) > 0):
        add_msg = 'add '

        for file in new_files:
            dir_list.append(file)
            # current_hashes[file] = hashed.get_hash('./temp/'+file)
            current_hashes[file] = hashed.get_hash(dir_path + '/' + file)
            # if file in gl_del:
            #     gl_del.remove(file)

        for file in new_files:
            add_msg += str(file) + ' '
            ssh = createSSHClient(ip_add, '22', 'nilesh', '041997')
            scp = SCPClient(ssh.get_transport())
            # scp.put('./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
            scp.put(dir_path + '/' + file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
            scp.close()
        s.sendall(bytes(add_msg, 'UTF-8'))

def send_modified_files(modified_files, s):
    if(len(modified_files) > 0):
        # add_msg = 'modified '
        print(modified_files)
        msg = (master.add_modified_file(modified_files))
        
        for file in modified_files:
            # add_msg += str(file) + ' '
            ssh = createSSHClient(ip_add, '22', 'nilesh', '041997')
            scp = SCPClient(ssh.get_transport())
            # scp.put('./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
            scp.put(dir_path + '/' + file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
            scp.close()
        
        modified_files.clear()
        # s.sendall(bytes(add_msg, 'UTF-8'))

def dir_scanner(s):
    # temp = os.listdir('./temp')
    temp = os.listdir(dir_path)
    new_files = [file for file in temp if file not in dir_list]
    deleted_files = [file for file in dir_list if file not in temp]
    modified_files = []
    for file in temp:
        # hash_of_file = hashed.get_hash('./temp/'+file)
        hash_of_file = hashed.get_hash(dir_path + '/' + file)
        if(file in dir_list and hash_of_file!=current_hashes[file]):
            modified_files.append(file)
            print(file,hash_of_file,current_hashes[file])
        current_hashes[file] = hash_of_file 
    delete_file(deleted_files, s)
    detect_deleted_file_from_master()    
    add_file(new_files,s)
    detect_new_files_from_master()
    send_modified_files(modified_files,s)
    detect_modified_files_from_master()

    

def detect_deleted_file_from_master():
    # print(ip)
    msg = (master.check_deleted_file())
    if msg:
        print(msg)
        file_list = msg.split(' ')
        for file in file_list:
            # file_path = './temp/' + file
            file_path = dir_path + '/' + file
            if file in list(dir_list):
                os.remove(file_path)
                dir_list.remove(file)
        # time.sleep(4)


def detect_new_files_from_master():
    # pdb.set_trace()
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
                scp.get(local_path=dir_path+'/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                scp.close()

def detect_modified_files_from_master():   
    msg = (master.check_modified_file())     
    # print("msg",msg)
    if msg:
        # print(msg)
        file_list = msg.split(' ')
        for file in file_list:
            if file in dir_list:
                print(file)
                ssh = createSSHClient( ip_add, '22', 'nilesh', '041997')
                scp = SCPClient(ssh.get_transport())
                # os.remove('./temp/'+file)
                os.remove(dir_path + '/' + file)
                # scp.get(local_path='./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                scp.get(local_path=dir_path+'/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                scp.get(local_path=dir_path+'/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                scp.get(local_path=dir_path+'/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                # scp.get(local_path='./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                # scp.get(local_path='./temp/'+file, remote_path = '/home/nilesh/Documents/Distributed_Systems/FileSyncron/temp/'+file, recursive=False)
                
                scp.close()
                # current_hashes[file] = hashed.get_hash('./temp/'+file)
                current_hashes[file] = hashed.get_hash(dir_path+'/'+file)
                

def Main1():
    global master
    master = Pyro5.api.Proxy('PYRO:file_syncron@' + ip_add + ':9001')

    port = 8085
    # pdb.set_trace()
    global s 
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
    s.close()


dir_path = sys.argv[0]
ip_add = sys.argv[1]

connected = False
while not connected:
    try:
        Main1()
        connected = True
    except:
        connected = False
        time.sleep(2)