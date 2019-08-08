from collections import OrderedDict


class Transaction:
    def __init__(self, sender, public_key, signature, recipient, amount):
        self.sender = sender
        self.public_key = public_key
        self.signature = signature
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return str(self.__dict__)

    def to_ordered_dict(self):
        return OrderedDict([
            ('sender', self.sender),
            ('public_key', self.public_key),
            ('signature', self.signature),
            ('recipient', self.recipient),
            ('amount', self.amount),
        ])
