This is a FTP application that implements TCP reliability over UDP sockets.
Reliability is guarenteed using a sliding window and selective repeat algorithm for re-sending packets that did not send the server back an ACK due to either corrupted data or a timeout on the packet
The window size is static at 5 packets.
Packet timeout has been set to 0.5 seconds.

Notes before executing program:
****receiver.py must be run before sender.py *****
* receiver.py will open a file with the same name as the file being sent to it,  with "New" 
  appended to the front of the file, so both sender and receiver python files may be in the same directory

Executing my files:
* python3 recevier.py -p <port_number>   
* python3 sender.py -f <filename> -a <ip_address> -p <port_number> -e <error_rate>
   0 <= error_rate <= 100 and it MUST be included in execution. error_rate determines the 
   % chance that a message will be given an invalid checksum, use 0 to test without this functionality 

command_line arguments may be in any order, but ALL must be present
port_number's when executing each file must equal  
