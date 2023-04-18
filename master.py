# import socket programming library
import socket
import os
import Pyro5.api
import paramiko
from paramiko import SSHClient
from scp import SCPClient
# import thread module
from _thread import *
import threading
# print_lock = threading.Lock()
ip_list = dict()
# dir_list = []
# del_file = {}

@Pyro5.api.expose
class Master(object):
    # @classmethod
    def __init__(self):
        self.del_files = dict()
        self.dir_list = []
        self.modified_files=dict()
        # self.dir_list = []

    def check_deleted_file(self):

        ip = Pyro5.api.current_context.client_sock_addr[0]
        temp = []
        for k in list(self.del_files.keys()):
            if ip not in self.del_files[k]:
                temp.append(k)
                self.del_files[k].append(ip)
            # del_file[k]+=1

                if len(self.del_files[k]) == len(ip_list):
                    print(self.del_files[k])
                    # print("==========", k)
                    # self.del_files.pop(k)
                    del self.del_files[k]
                    obj.dir_list.remove(k)
                    # print("------------", len(self.del_files))
                    print('--> Deleted',k)

        return ' '.join(temp)
    
    def check_modified_file(self):
        ip = Pyro5.api.current_context.client_sock_addr[0]
        temp = []
        for k in list(self.modified_files.keys()):
            if ip not in self.modified_files[k]:
                temp.append(k)
                self.modified_files[k].append(ip)
            # del_file[k]+=1

                if len(self.modified_files[k]) == len(ip_list):
                    print("Files Modified : " , self.modified_files[k])
                    del self.modified_files[k]

        return ' '.join(temp)

    def add_modified_file(self, modified_file_list):
        ip = Pyro5.api.current_context.client_sock_addr[0]
        for file in modified_file_list:
            print("request for modification: ", file, "by", ip)
            # self.modified_files.append(file)
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
    while True:
        temp = os.listdir('./temp')
        new_files = [file for file in temp if file not in obj.dir_list]
        for i in new_files:
            obj.dir_list.append(i)

# thread function
def threaded(c,ip):
    log_file = open('log','a')
    while True:
        data = c.recv(8192).decode('utf-8')
        msg = data.split(' ')
        print(msg)
        # msg.pop
        if msg[0] == 'delete':
            del msg[-1]
            for i in msg[1:]:
                print(i,obj.dir_list)
                log_msg = 'delete ' + i + ' ' + ip
                log_file.write(log_msg)
                obj.del_files[i]= [ip]
                print('./temp/'+i)
                os.remove('./temp/' + i)

        elif msg[0] == 'add':
            del msg[-1]
            for i in msg[1:]:
                if i not in obj.dir_list:
                    log_msg = 'add ' + i + ' ' + ip
                    log_file.write(log_msg)
                    obj.dir_list.append(i)
            print(obj.dir_list)
        # data received from client
        if not data:
            print('Bye')
            break
    # connection closed
    ip_list.pop(ip)
    log_file.close()
    c.close()


def Main():
    # if('log' in os.listdir('./temp')){
    #     os.remove('./temp/log')
    # }
    port = 8085
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")
    start_new_thread(dir_scanner, ())
    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()
        data = c.recv(2048).decode('utf-8')
        data1 = data.split(' ')
        # lock acquired by client
        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        addr
        ip_list[addr[0]] = data1
        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,addr[0]))
        print(ip_list)
    s.close()

def pyro_func(obj):
    daemon = Pyro5.api.Daemon(host='0.0.0.0', port=9002)
    uri = daemon.register(obj,"file_syncron")
    print("URI:",uri)
    Pyro5.api.serve({}, host="0.0.0.0", port=9002, daemon=daemon, use_ns=False, verbose=True)

if __name__ == '__main__':
    obj = Master()
    start_new_thread(pyro_func, (obj,))
    Main()
    



