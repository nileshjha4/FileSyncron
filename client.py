import socket, time
import pdb,os
import paramiko, sys
import Pyro5.api
from paramiko import SSHClient
from scp import SCPClient
import time
import hashed
from config import *

ip = socket.gethostbyname_ex(socket.gethostname())[-1]
current_hashes = {}
dir_list = []

def createSSHClient(server, port, user, password):
    """
        Description: This function returns the client object connected to the server
        Input: IP address of host, port of host, host username, host password
        Output: Object of client connected to the server        
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, look_for_keys = False, allow_agent = False)
    return client

def delete_file(deleted_files, s):
    """
        Description: This function creates a string of all file names which has to be deleted on client side and send it to client side.
        Input: list of deleted files, socket connection
        Output: No output is returned.        
    """
    if(len(deleted_files) > 0):
        del_msg = 'delete '

        for file in deleted_files:
            dir_list.remove(file)

        for file in deleted_files:
            del_msg +=  str(file) + ' '
        s.sendall(bytes(del_msg, 'UTF-8'))
    
def add_file(new_files, s):
    """
        Description: This function creates a string of all file names which has to be added on client side and send it to client.
        Input: list of added files, socket connection
        Output: No output is returned. 
    """
    if(len(new_files) > 0):
        add_msg = 'add '
        for file in new_files:
            dir_list.append(file)
            current_hashes[file] = hashed.get_hash(LOCAL_PATH + '/' + file)

        for file in new_files:
            add_msg +=  str(file) + ' '
            ssh = createSSHClient(ip_add, '22', USER_NAME, PASSWORD)
            scp = SCPClient(ssh.get_transport())
            scp.put(LOCAL_PATH + '/' + file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
            scp.close()

        s.sendall(bytes(add_msg, 'UTF-8'))

def send_modified_files(modified_files, s):
    """
        Description: This function sends files which get modified to all other clients .
        Input: list of modified files, socket connection
        Output: No output is returned. 
    """
    if(len(modified_files) > 0):
        msg = (master.add_modified_file(modified_files))        
        for file in modified_files:
            ssh = createSSHClient(ip_add, '22', USER_NAME, PASSWORD)
            scp = SCPClient(ssh.get_transport())
            scp.put(LOCAL_PATH + '/' + file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
            scp.close()
        
        modified_files.clear()

def dir_scanner(s):
    """
        Description: This function checks whether any file is deleted, added or modified in its repository.
        Input: socket connection
        Output: No output is returned. 
    """
    volume = os.listdir(LOCAL_PATH)
    new_files = [file for file in volume if file not in dir_list]
    deleted_files = [file for file in dir_list if file not in volume]
    modified_files = []
    for file in volume:
        hash_of_file = hashed.get_hash(LOCAL_PATH + '/' + file)
        if file in dir_list and hash_of_file != current_hashes[file]:
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
    """
        Description: This function checks if any file gets deleted in master's directory then delete it in client's directory also.
    """
    msg = (master.check_deleted_file())
    if msg:
        file_list = msg.split(' ')
        for file in file_list:
            file_path = LOCAL_PATH + '/' + file
            if file in list(dir_list):
                print("File deleted -> ", file)
                os.remove(file_path)
                dir_list.remove(file)
 
def detect_new_files_from_master():
    """
        Description: This function checks if any file gets added in master's directory then add it in client's directory also.
    """
    msg = (master.check_added_file())
    if msg:
        file_list = msg.split(' ')
        for file in file_list:
            if file not in dir_list:
                print("File added -> ", file)
                ssh = createSSHClient(ip_add, '22', USER_NAME, PASSWORD)
                scp = SCPClient(ssh.get_transport())
                # scp.get(LOCAL_PATH = './volume/'+file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
                scp.get(LOCAL_PATH = LOCAL_PATH+'/'+file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
                scp.close()

def detect_modified_files_from_master():  
    """
        Description: This function checks if any file gets modified in master's directory by calculating hash then update it in client's directory also.
    """ 
    msg = (master.check_modified_file())  
    if msg:
        file_list = msg.split(' ')
        for file in file_list:
            if file in dir_list:
                print("File Modified -> " + file)
                ssh = createSSHClient( ip_add, '22', USER_NAME, PASSWORD)
                scp = SCPClient(ssh.get_transport())
                os.remove(LOCAL_PATH + '/' + file)
                scp.get(local_path = LOCAL_PATH+'/'+file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
                scp.get(local_path = LOCAL_PATH+'/'+file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
                scp.get( local_path = LOCAL_PATH+'/'+file, remote_path = REMOTE_PATH + '/' +file, recursive = False)
                scp.close()
                current_hashes[file] = hashed.get_hash(LOCAL_PATH+'/'+file)
                

def check_initial_dir():
    if(os.path.exists("./volume")):
        return
    else:
        curr_path = str(os.getcwd())
        print(curr_path)
        direct = "volume"
        path = os.path.join(curr_path, direct)
        mode =0o6666
        os.mkdir(path, mode)


def Main1():
    global master
    master = Pyro5.api.Proxy('PYRO:file_syncron@' + ip_add + ':9001')
    global s 
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # connect to server on local computer
    s.connect((ip_add,port))
    print("Connection created")
    # s.sendall(bytes("vishal Vishal8199 " + os.getcwd() +"/volume",'UTF-8'))
    ssh = createSSHClient( ip_add, '22', USER_NAME, PASSWORD)
    scp = SCPClient(ssh.get_transport())
    scp.get(local_path = './', remote_path = REMOTE_PATH, recursive = True)
    scp.put(LOCAL_PATH, remote_path = REMOTE_PATH[:REMOTE_PATH.rfind('/')], recursive = True)
    scp.close()  
    print("All files uploaded from Master")
    while True:
        dir_scanner(s)
    s.close()

ip_add = sys.argv[1]
port = int(sys.argv[2])

check_initial_dir()

connected = False
while not connected:
    try:
        Main1()
        connected = True
    except:
        connected = False
        time.sleep(2)

Main1()