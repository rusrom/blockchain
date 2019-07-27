import json
from hashlib import sha256


def hash_block(block):
    block_to_dictionary = block.__dict__.copy()
    return sha256(json.dumps(block_to_dictionary, sort_keys=True).encode()).hexdigest()
