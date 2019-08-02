from collections import OrderedDict


class Transaction:
    def __init__(self, sender, signature, recipient, amount):
        self.sender = sender
        self.signature = signature
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return str(self.__dict__)

    def to_ordered_dict(self):
        return OrderedDict([
            ('sender', self.sender),
            ('signature', self.signature),
            ('recipient', self.recipient),
            ('amount', self.amount),
        ])
