import Pyro5.api
import threading

@Pyro5.api.expose
class MyClass:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
        
    def my_method(self, arg3):
        print(self.arg1, self.arg2)
        return self.arg1 + self.arg2 + arg3

my_instance = MyClass(10, 20)

daemon = Pyro5.api.Daemon(host='0.0.0.0', port=9001)
uri = daemon.register(my_instance,"my_instance")
print(uri)
Pyro5.api.serve(
    {},
    daemon=daemon, host='0.0.0.0', port=9001, use_ns=False, verbose=True
)

