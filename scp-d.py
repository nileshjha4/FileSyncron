if __name__ == "__main__":
    # Parse and check the arguments
    ssh = ssh('10.2.133.88', 'purnima', 'Ketan1411')
    ssh.scp.put("Valigrind_BB.py") # This works perfectly fine
    ssh.scp.put("temp", recursive=True) # IOError over here Is a directory
    ssh.sendCommand('ls')