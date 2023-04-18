# saved as greeting-client.py
import Pyro4

ipAddressServer = "10.2.133.88" # TODO add your server remote IP here

# Works for Python3, see edit above for notes on Python 2.x
name = input("What is your name? ").strip()

greetingMaker = Pyro4.core.Proxy('PYRO:Greeting@' + ipAddressServer + ':9090')
print(greetingMaker.get_fortune(name))