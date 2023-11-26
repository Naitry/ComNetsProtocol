We have designed a basic TCP based protocol to send messages back to and run control commands on server. The implementation is in python for both the client and server

This was designed to be a lightweight way to send basic messages. The server will archive messages with timestamps from multiple simultaneous clients in log files. TCP makes it easy to keep everything reliable as we don't need low latency.

The protocol uses 4 byte headers to either fully encapsulated commands or indicate the start of a larger message

## Handshake
When a client connects to the server the server will expect a header only message consisting of the "PING" header and will respond with a "PONG" header 
This is the initial handshake which will occur at the beginning of every connection

## Post Handshake
At this point the sure has three choices
1. User sends a regular message
   1. A message will be sent with a "MESG" header followed by a space then string which was sent
   2. The client will receive an echo of the message to show what has been written to the server logs
2. User enters "terminate" to indicate program termination
   1. The program prompt will the user to enter a password then send a message with a "TERM" header followed by a space then the password entered.
   2. The client program will then react according to the response from the server, with the response will be one of the following header only responses:
      1. "PWOK": password was correct, the server has been closed and the client will now close
      2. "PWNO": password was wrong, the server is still running and the client will continue to run
      3. "PWIV": password was formatted incorrectly, the server is still running and the client will continue to run
3. User closes the program
   1. The connection is closed, the server will still be running

### Security Disclaimer
A note on security; this protocol uses password and sends messages, but does not encrypt anything. This is not truly secure at all and could easily be broken. It would require significantly more effort to do this and I think that is beyond the scope of this project. 