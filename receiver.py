import binascii
from socket import *
import argparse
import pickle

from message import Message
from receiverBuffer import Window

# Gets command line arguments
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="port")
    args = parser.parse_args()
    args.port = int(args.port)
    return args

# Receives initial Syn message, sets initial sequence number, and sends SynAck message back to sender
def establish_connection(receiver_socket):
    syn_message, sender_address = receiver_socket.recvfrom(2048)
    syn_message = pickle.loads(syn_message)
    synack_message = Message("ack", syn_message.sequence + 1)
    print("Sending synAck for initial connection")
    receiver_socket.sendto(pickle.dumps(synack_message), sender_address)
    return synack_message.sequence

# Gets the name of the file being sent to the receiver
def get_file_name(receiver_socket):
    file_name, sender_address = receiver_socket.recvfrom((2048))
    file_name = "New " + str(pickle.loads(file_name))
    return file_name

def main():
    args = get_args()
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(("", args.port))
    sequence_number = establish_connection(receiver_socket)
    file_name = get_file_name(receiver_socket)
    file = open(file_name, "wb")
    # Create a sliding window of size 5
    window = Window(5)
    # Set socket to non-blocking
    receiver_socket.settimeout(0)

    while True:
        # While the window is able to receive more messages
        while window.has_room():
            # Read from socket as long as data is immediately available
            try:
                message, sender_address = receiver_socket.recvfrom(2048)
                message = pickle.loads(message)
                if message.message_type == "end":
                    window.read_data(sequence_number, file)
                    receiver_socket.close()
                    exit(0)
                window.receive_message(message, receiver_socket, sender_address)
            except BlockingIOError:
                break
        # Check list of received messages and see if next expected message was received
        sequence_number = window.read_data(sequence_number, file)
if __name__ == "__main__":
    main()