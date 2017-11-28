import random
import binascii
import sys
import time

# Class that holds data and functions to operate on messages
class Message:
    def __init__(self, message_type, sequence):
        self.message_type = message_type
        self.sequence = sequence
        self.data = None
        self.checksum = None
        self.send_time = None

    # Generates and sets checksum using binascii module
    def generate_checksum(self, error_rate):
        if random.randint(0, 99) < error_rate:
            self.checksum = 0
        else:
            self.checksum = binascii.crc32(self.data) & 0xffffffff

    # Generates checksum and verifies it against the message's checksum
    def validate_checksum(self):
        crc = binascii.crc32(self.data) & 0xffffffff
        if crc != self.checksum:
            return False
        else:
            return True

    # Calculates how many bytes of data can be sent in this message
    def calculate_remainder(self):
        message_size = sys.getsizeof(self.message_type)
        sequence_size = sys.getsizeof(self.sequence)
        # Checksum is at most 32 bytes (Found through testing on a console)
        checksum_size = 32
        return 1472 - message_size - sequence_size - checksum_size

    def set_data(self, data):
        self.data = data

    def set_send_time(self, send_time):
        self.send_time = send_time

    # Check if sent packet has not received an ack in 500ms
    def check_timeout(self):
        if ((time.time() - self.send_time) * 1000) > 500:
            return True
        return False

    def get_sequence(self):
        return self.sequence