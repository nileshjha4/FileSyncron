import Pyro5.api

my_proxy = Pyro5.api.Proxy('PYRO:my_instance@0.0.0.0:9001')
result = my_proxy.my_method(30)
print(result)

