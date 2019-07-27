import json
from hashlib import sha256


def hash_block(block):
    # Convert Bloc Class to dictionary
    block_to_dictionary = block.__dict__.copy()

    # Convert block Transactions Classes to OrderedDicts
    block_to_dictionary['transactions'] = [
        tx.to_ordered_dict()
        for tx in block_to_dictionary['transactions']
    ]

    return sha256(json.dumps(block_to_dictionary, sort_keys=True).encode()).hexdigest()
