import pickle
import argparse
from socket import *
import os
import time

from message import Message
from senderWindow import Window

# Gets command line arguments
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="file_name")
    parser.add_argument("-a", dest="ip_address")
    parser.add_argument("-p", dest="port")
    parser.add_argument("-e", dest="error_rate")
    args = parser.parse_args()
    args.port = int(args.port)
    args.error_rate = int(args.error_rate)
    return args

# Sends initial Syn message, sets initial sequence number, and waits for synAck from receiver
def establish_connection(sender_socket, destination):
    syn_message = Message("start", 0)
    print("Requesting initial connection")
    sender_socket.sendto(pickle.dumps(syn_message), destination)
    synack_message, sender_address = sender_socket.recvfrom(2048)
    synack_message = pickle.loads(synack_message)
    return synack_message.sequence

# Helper function to create a new message object to send to receiver
def create_message(file, sequence_number, error_rate):
    message = Message("data", sequence_number)
    data_size = message.calculate_remainder()
    data = file.read(data_size)
    message.set_data(data)
    # Make checksum invalid a given percentage of the time
    message.generate_checksum(error_rate)
    return message


def main():
    args = get_args()
    destination = (args.ip_address, args.port)
    file = open(args.file_name, "rb")
    file_size = os.path.getsize(args.file_name)
    sender_socket = socket(AF_INET, SOCK_DGRAM)
    sequence_number = establish_connection(sender_socket, destination)
    error_rate = args.error_rate
    # Create sliding window of size 5
    window = Window(5)
    # Sending file name to receiver
    sender_socket.sendto(pickle.dumps(args.file_name), destination)
    # Make socket non-blocking
    sender_socket.settimeout(0)
    print("Connection established with receiver, ready to send data")

    # Loop until file size is 0 and all packets have been acked
    while file_size > 0 or sum(isinstance(m, Message) for m in window.sent) > 0:
        # While window has room to send packets, create and send packets
        while window.has_room() and file_size > 0:
            message = create_message(file, sequence_number, error_rate)
            file_size -= len(message.data)
            sequence_number += len(message.data)
            message.set_send_time(time.time())
            window.sent[window.next] = message
            window.increment_next()
            sender_socket.sendto(pickle.dumps(message), destination)
        # Receive acks from receiver until there is no data available to be read from socket.
        while True:
            try:
                ack_message, sender_address = sender_socket.recvfrom(2048)
                ack_message = pickle.loads(ack_message)
                window.receive_ack(ack_message.sequence)
            except BlockingIOError:
                break
        # Checking and re-sending any messages that have timed out
        for message in window.sent:
            if message is not None and message.check_timeout():
                # Only resend messages that have not already been acked, but are still in the sent list
                if message.sequence not in window.ack:
                    print("Error: segment # " + str(message.sequence) + " resent - timeout")
                    message.set_send_time = time.time()
                    message.generate_checksum(error_rate)
                    sender_socket.sendto(pickle.dumps(message), destination)

    # Send end message and close socket
    end_message = Message("end", sequence_number)
    sender_socket.sendto(pickle.dumps(end_message), destination)
    sender_socket.close()


if __name__ == "__main__":
    main()
