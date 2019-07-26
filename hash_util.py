import json
from hashlib import sha256


def hash_block(block):
    return sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
