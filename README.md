The project is a basic python implementation of a tcp socket
It requires nothing other than python 3.x to run the python version of the server

## Server
The server can be ran from the command line with:

```
python server.py
```
## Client
The client can be ran in the same way with:
You will have the options to stop, start, and exit
Start will start the server
Stop will stop the server without closing the program
Exit will stop the server and close the program
The server IP, Port, and password for termination are designated in the config file

```
python client.py
```
The client and server processes can both be killed by sending the message "terminate" from the client to the server and providing a corrent password
The server IP and Port are designated in the config file
