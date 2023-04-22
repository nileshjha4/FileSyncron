# FileSyncron
FileSyncron is a straightforward tool for maintaining folder synchronization among computers linked via a network. File Synchronisation between master and client refers to multiple client devices having common files, updated and consistent with each other. The goal of file synchronization is to ensure that the same version of a file is available on all connected devices, so that users can access and work on the file from any of their devices without worrying about version control or manually copying files between devices. This can be especially useful for teams or individuals who work on the same files across multiple devices or locations.

## Running the application

#### Installing the dependencies:
Cmd: `pip3 install requirements.txt`

#### Master:
Cmd: `python3 master.py port_number`

#### Client:
Cmd: `python3 client.py master_ip-address port_number`

#### Configuring environment variables:
We are using scp to transfer files between client to master which underthehood uses ssh connection, hence we need to configure master's credentials into environment variables so as to prevent leaking your confidential information.

## Contribution/Suggestions
Feel free to test, fork and give suggestions. (Note: please do not use important files/directories to experiment with this application.)

