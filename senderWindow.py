from message import Message

# Class that represents a sliding window
class Window:
    def __init__(self, size):
        self.size = size
        self.base = 0
        self.next = 0
        self.sent = [None] * 5
        self.ack = []

    # Check if sliding window has room for more packets to be sent
    def has_room(self):
        return sum(isinstance(m, Message) for m in self.sent) < self.size

    # Increment next by 1, next will loop around to 0 once it is larger than 4
    def increment_next(self):
        if self.next + 1 > (self.size - 1):
            self.next = (self.next + 1) % self.size
        else:
            self.next += 1

    # Increment base by 1, base will loop around to 0 once it is larger than 4
    def increment_base(self):
        if self.base + 1 > (self.size - 1):
            self.base = (self.base + 1) % self.size
        else:
            self.base += 1

    # Once an ack is received by receiver, place sequence number in ack array if it is not present already
    def receive_ack(self, sequence_number):
        if sequence_number not in self.ack:
                self.ack.append(sequence_number)
        self.alter_base()

    # Called by receive_ack, Starts at base on sliding window and removes packets that have been acked
    def alter_base(self):
        message = self.sent[self.base]
        while message is not None and message.sequence in self.ack:
            self.ack.remove(message.sequence)
            self.sent[self.base] = None
            self.increment_base()
            message = self.sent[self.base]