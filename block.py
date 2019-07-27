from time import time


class Block:
    def __init__(self, index, previous_hash, transactions, nonce, timestamp=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = timestamp

    def __repr__(self):
        return f'<Block Class index: {self.index}, prev_hash: {self.previous_hash}, txs: {self.transactions}, nonce: {self.nonce}>'
