# import socket programming library
import socket
import os,sys
import Pyro5.api
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from _thread import *
import threading
ip_list = dict()
ip_list_old = []

@Pyro5.api.expose
class Master(object):
    # @classmethod
    def __init__(self):
        self.del_files = dict()
        self.dir_list = []
        self.modified_files=dict()

    def check_deleted_file(self):
        ip = Pyro5.api.current_context.client_sock_addr[0]
        temp = []
        for k in list(self.del_files.keys()):
            if ip not in self.del_files[k]:
                temp.append(k)
                self.del_files[k].append(ip)

                if len(self.del_files[k]) == len(ip_list):
                    os.remove('./volume/' + k)
                    del self.del_files[k]
                    print('--> Deleted File', k)

        return ' '.join(temp)
    
    def check_modified_file(self):
        ip = Pyro5.api.current_context.client_sock_addr[0]
        temp = []
        for k in list(self.modified_files.keys()):
            if ip not in self.modified_files[k]:
                temp.append(k)
                self.modified_files[k].append(ip)
                if len(self.modified_files[k]) == len(ip_list):
                    print("-->Files Modified : " , k)
                    del self.modified_files[k]

        return ' '.join(temp)

    def add_modified_file(self, modified_file_list):
        ip = Pyro5.api.current_context.client_sock_addr[0]
        for file in modified_file_list:
            log_file = open('log','a')
            log_file.write("Modified " + str(file) + " " + str(ip) + "\n")
            log_file.close()
            print("--> Request for modification:", file, "by", ip)
            self.modified_files[file] = [ip]
        return 'Got_modified'
    
    def check_added_file(self):
        return ' '.join(self.dir_list)
    
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, look_for_keys=False, allow_agent=False)
    return client

def dir_scanner():
    # while True:
    temp = os.listdir('./volume')
    new_files = [file for file in temp if file not in obj.dir_list]
    for i in new_files:
        obj.dir_list.append(i)

def threaded(c,ip):
    while True:
        data = c.recv(8192).decode('utf-8')
        msg = data.split(' ')
        print(msg)
        if msg[0] == 'delete':
            del msg[-1]
            for i in msg[1:]:
                print(i,obj.dir_list)
                log_msg = 'delete ' + i + ' ' + ip + '\n'
                log_file = open('log','a')
                log_file.write(log_msg)
                log_file.close()
                obj.del_files[i]= [ip]
                print('./volume/'+i)
                obj.dir_list.remove(i)

        elif msg[0] == 'add':
            del msg[-1]
            for i in msg[1:]:
                if i not in obj.dir_list:
                    log_msg = 'add ' + i + ' ' + ip + '\n'
                    log_file = open('log','a')
                    log_file.write(log_msg)
                    log_file.close()
                    obj.dir_list.append(i)
            print(obj.dir_list)
        if not data:
            print('Bye')
            break
    ip_list.pop(ip)
    log_file = open('log','a')
    log_file.write("Disconnected " + str(ip) + "\n")
    log_file.close()
    c.close()

def Main():
    # port = 54321
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(5)
    print("Master is listening at port:", port)
    dir_scanner()
    while True:
        c, addr = s.accept()
        data = c.recv(2048).decode('utf-8')
        data1 = data.split(' ')
        print('Connected to :', addr[0], ':', addr[1])
        log_file = open('log', 'a')
        log_file.write("Connected " + str(addr[0])+"\n")
        log_file.close()
        # addr
        ip_list[addr[0]] = data1
        start_new_thread(threaded, (c,addr[0]))
        print(ip_list)
    s.close()

def pyro_func(obj):
    daemon = Pyro5.api.Daemon(host='0.0.0.0', port=9001)
    uri = daemon.register(obj,"file_syncron")
    # print(uri)
    print("1")
    Pyro5.api.serve({}, host='0.0.0.0', port=9001, daemon=daemon, use_ns=False, verbose=True)
    print("2")

# if __name__ == '__main__':
obj = Master()
port = int(sys.argv[1])
start_new_thread(pyro_func, (obj,))
Main()
    



