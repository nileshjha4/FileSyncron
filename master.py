# import socket programming library
import socket
import os
import Pyro4
import paramiko
from paramiko import SSHClient
from scp import SCPClient
# import thread module
from _thread import *
import threading
# print_lock = threading.Lock()
ip_list = dict()
dir_list = []
del_file = {}
@Pyro4.expose
class Master(object):
    def check_deleted_file(self, ip):
        # port = 8084
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.bind(('0.0.0.0', port))
        # c, addr = s.accept()
        # del_file = c.recv(8192).decode('utf-8')
        # # file_list = msg.split(' ')[1:]
        # # for file in file_list:
        # #     file_path = './temp/' + file
        # #     try:
        # #         os.remove(file_path)
        # #     except FileNotFoundError:
        # #         print(f"File {file_path} does not exist.")
        # s.close()
        temp = []
        for k,v in del_file.items():
            temp.append(k)
            if ip not in del_file[k]:
                del_file[k].append(ip)
            # del_file[k]+=1
            if len(del_file[k]) == len(ip_list)-1:
                del_file.pop(k)

        return ' '.join(temp)
        # return del_file.join(' ')
    
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, look_for_keys=False, allow_agent=False)
    return client

def dir_scanner():
    while True:
        temp = os.listdir('./temp')
        new_files = [file for file in temp if file not in dir_list]
        for i in new_files:
            dir_list.append(i)
        if len(new_files)!=0:
            print(new_files)
            for file in new_files:
                # print(file)
                for current_ip,data in ip_list.items():
                    # print(current_ip,data)
                    ssh = createSSHClient( current_ip,'22', data[0], data[1])
                    scp = SCPClient(ssh.get_transport())
                    scp.put('./temp/'+file, remote_path = data[2], recursive=True)
                    scp.close()

# thread function
def threaded(c,ip):
    while True:
        data = c.recv(8192).decode('utf-8')
        msg = data.split(' ')
        if msg[0] == 'delete':
            for i in msg[1:]:
                del_file[i]= []

        # data received from client
        if not data:
            print('Bye')
            # lock released on exit            # print_lock.release()
            break

        # reverse the given string from client
        # data = data[::-1]

        # # send back reversed string to client
        # c.send(data.encode('utf-8'))

    # connection closed
    ip_list.pop(ip)
    c.close()


def Main():
    host = ""

    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 8083
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

def pyro():
    Pyro4.Daemon.serveSimple({
    Master: 'Master',
    }, host="0.0.0.0", port=9095, ns=False, verbose=True)

if __name__ == '__main__':
    start_new_thread(pyro, ())
    Main()
    



