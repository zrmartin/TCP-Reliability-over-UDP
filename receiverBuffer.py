from message import Message
import pickle

# Class to represent receiver sliding window
class Window:
    def __init__(self, size):
        self.size = size
        self.recv = []

    # Check if window has room to receive more packets
    def has_room(self):
        return sum(isinstance(m, Message) for m in self.recv) < self.size

    # Called whenever a packet is received
    def receive_message(self, message, socket, address):
        if message.validate_checksum():
            # If the packet is not already in the recv list, add it
            if not any(m.sequence == message.sequence for m in self.recv):
                print("received packet starting with " + str(message.sequence))
                self.recv.append(message)
                ack = Message("ack", message.sequence)
                socket.sendto(pickle.dumps(ack), address)
        else:
            print("Error: CRC error in segment beginning with " + str(message.sequence) + " segment dropped")

    # Called after done receiving data from socket
    def read_data(self, sequence_number, file):
        while len(self.recv) > 0:
            # Sort the list of messages by sequence numbers
            self.recv = sorted(self.recv, key=Message.get_sequence)
            # Grab the message with the lowest sequence number
            message = self.recv[0]
            # Next expected packet has been received and is ready to write to file
            if message.sequence == sequence_number:
                file.write(message.data)
                print("Read packet starting with: " + str(sequence_number))
                # Increase sequence_number to next expecting sequence_number
                sequence_number += len(message.data)
                del self.recv[0]
            # If duplicate messages sent for same packet, discard
            elif message.sequence < sequence_number:
                print("Error: Segment " + str(message.sequence) + " duplicate")
                del self.recv[0]
            else:
                break
        return sequence_number
