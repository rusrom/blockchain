import json
import pickle
from hashlib import sha256

from hash_util import hash_block
from block import Block
from transaction import Transaction


MINING_REWARD = 10
DIFFICULTY = '00'

blockchain = []
open_transactions = []
owner = 'rusrom'
participants = {owner}


def load_data():
    global blockchain
    global open_transactions

    try:
        with open('blockchain.txt') as f:
            file_content = f.readlines()
    except FileNotFoundError:
        print('Genesis block innit...')
        genesis_block = Block(
            index=0,
            previous_hash='Genesis_Block',
            transactions=open_transactions[:],
            nonce=0
        )
        blockchain.append(genesis_block)
        return

    # Read data from dump file
    corrected_blockchain_dump = []
    for block_dump in json.loads(file_content[0]):
        block = Block(
            index=block_dump['index'],
            previous_hash=block_dump['previous_hash'],
            transactions=[
                Transaction(
                    sender=tx['sender'],
                    recipient=tx['recipient'],
                    amount=tx['amount']
                )
                # OrderedDict([
                #     ('sender', tx['sender']),
                #     ('recipient', tx['recipient']),
                #     ('amount', tx['amount'])
                # ])
                for tx in block_dump['transactions']
            ],
            nonce=block_dump['nonce'],
            timestamp=block_dump['timestamp']
        )
        corrected_blockchain_dump.append(block)
    blockchain = corrected_blockchain_dump[:]

    open_transactions = [
        Transaction(
            sender=tx['sender'],
            recipient=tx['recipient'],
            amount=tx['amount']
        )
        for tx in json.loads(file_content[1])
    ]
    # open_transactions = [
    #     OrderedDict([
    #         ('sender', tx['sender']),
    #         ('recipient', tx['recipient']),
    #         ('amount', tx['amount'])
    #     ])
    #     for tx in json.loads(file_content[1])
    # ]


def save_data():
    # Prepare before saving to JSON format string
    blockchain_blocks_to_dict = [block.__dict__.copy() for block in blockchain]

    for block in blockchain_blocks_to_dict:
        transactions_to_dict = [tx.to_ordered_dict() for tx in block['transactions']]
        block['transactions'] = transactions_to_dict

    print('>>>>>>>>>>>>>>>>', blockchain_blocks_to_dict)

    open_transactions_to_dict = [tx.__dict__.copy() for tx in open_transactions]

    with open('blockchain.txt', 'w') as f:
        f.write(json.dumps(blockchain_blocks_to_dict) + '\n')
        f.write(json.dumps(open_transactions_to_dict))


def load_data_picle():
    with open('blockchain.p', 'rb') as f:
        file_content = pickle.loads(f.read())

    print(file_content)
    global blockchain
    global open_transactions

    blockchain = file_content['blockchain']
    open_transactions = file_content['open_transactions']


def save_data_pickle():
    with open('blockchain.p', 'wb') as f:
        save_data = {
            'blockchain': blockchain,
            'open_transactions': open_transactions
        }
        f.write(pickle.dumps(save_data))


def get_last_blockchain_value():
    '''Returns the last value of current blockchain'''
    if blockchain:
        return blockchain[-1]


def verify_transaction(transaction):
    '''Verify sender ability to do transaction
    If balance >= tx_amount
    '''
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount


def verify_transactions():
    '''Verify ALL open transaction in pull
    '''
    return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(recipient, amount, sender=owner):
    '''Append a new value as well as the last blockchain value to the blockchain
    Like adding transaction to the pool in real life
    Arguments:
        :sender: The sender(default=owner) of the coins
        :recipient: The recipient of the coins
        :amount: The amount of coins that should be sent
    '''
    transaction = Transaction(
        sender=sender,
        recipient=recipient,
        amount=amount
    )

    if verify_transaction(transaction):
        # Add transaction to open transactions
        open_transactions.append(transaction)

        # Add unique participant to set of all participants of blockchain
        # participants.add(sender)
        # participants.add(recipient)
        # participants.update([sender, recipient])

        # Dump blockchain and open transactions to file
        save_data()

        return True
    return False


def valid_proof(transactions, last_block_hash, proof):
    '''Check amount of leading zerroes in hash
    Only after getting True inside this function
    new block will be added to the blockchain'''
    guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_block_hash) + str(proof)).encode()
    guess_hash = sha256(guess).hexdigest()
    print(guess_hash)
    return guess_hash.startswith(DIFFICULTY)


def proof_of_work():
    '''Struggle with DIFFICULTY seeking correct proof'''
    last_block = blockchain[-1]
    last_block_hash = hash_block(last_block)

    proof = 0
    while not valid_proof(open_transactions, last_block_hash, proof):
        proof += 1
    return proof


def mine_block():
    # Reward transaction for miners
    reward_transaction = Transaction(
        sender='MINING_REWARD_BOT',
        recipient=owner,
        amount=MINING_REWARD
    )

    # IMPORTANT: Proof of Work should NOT INCLUDE REWARD TRANSACTION
    nonce = proof_of_work()

    # Add reward transaction
    open_transactions.append(reward_transaction)

    # Create block
    block = Block(
        index=len(blockchain),
        previous_hash=hash_block(blockchain[-1]),
        transactions=open_transactions[:],
        nonce=nonce
    )

    # Add block to blockchain
    blockchain.append(block)

    # Clear open transactions
    open_transactions.clear()

    # Dump blockchain and open transactions to file
    save_data()


def get_balance(participant):
    '''Get balance of participant coins
    Input amount - Outpu amount - Amount of coins in open transaction (in pull)
    '''
    tx_inputs = [
        tx.amount
        for block in blockchain
        for tx in block.transactions
        if tx.recipient == participant
    ]

    tx_outputs = [
        tx.amount
        for block in blockchain
        for tx in block.transactions
        if tx.sender == participant
    ]

    # Participant's All sending transactions that are in open_transactions(pool)
    tx_open = [
        tx.amount
        for tx in open_transactions
        if tx.sender == participant
    ]

    return sum(tx_inputs) - sum(tx_outputs) - sum(tx_open)


def get_user_choice():
    print(
        '''----------------------------
        Choose what do you want to do?
            1: Send transaction
            2: Mine block
            3: Show blockchain
            4: Show participants
            5: Check transaction validity
            6: Show participants balances
            7: Show open transactions (pool)
            q: Quit
        ----------------------------''')
    return input('Your choice: ')


def get_transaction_value():
    '''Returns the input of the user (transaction amount) as float'''
    tx_recipient = input('Enter the recipient of transaction: ')
    tx_amount = float(input('Enter transaction amount: '))
    return tx_recipient, tx_amount


def print_blockchain_elements():
    if not blockchain:
        print('No blockchaine yet')
    else:
        for block in blockchain:
            print(block)


def print_open_transactions():
    if not open_transactions:
        print('No open transactions yet')
    else:
        print('Open transactions:')
        for open_tx in open_transactions:
            print(open_tx)


def verify_chain():
    '''Verify each block['previous_block_hash'] vith calculated hash_block() of previous block'''
    for previous_block, block in enumerate(blockchain[1:]):
        # Verify previous block hash
        if block.previous_hash != hash_block(blockchain[previous_block]):
            print('Previous block hash is invalid')
            return False
        # Verify PoW of current block
        print('Verify chain > Validate PoW')
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.nonce):
            print('Proof of Work is invalid')
            return False
    return True


def show_participants():
    print(participants)


def show_participants_balances():
    '''Show balaces for all participants of blockchain'''
    for participant in participants:
        print(f'{participant}: {get_balance(participant)} coins')


# Load blockchain and open transaction from file
load_data()


while True:
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_recipient, tx_amount = get_transaction_value()
        if add_transaction(tx_recipient, tx_amount):
            print('Open transactions:', open_transactions)
        else:
            print('Transaction failed!')
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        show_participants()
    elif user_choice == '5':
        if open_transactions:
            if verify_transactions():
                print('All transactions are valid')
            else:
                print('[ERROR] There are invalid open transactions in pull')
        else:
            print('No one open transaction yet')
    elif user_choice == '6':
        show_participants_balances()
    elif user_choice == '7':
        print_open_transactions()
    elif user_choice == 'q':
        break
    else:
        print('Your input is invalid')
        continue

    if not verify_chain():
        raise Exception('[CRITICAL ERROR] Blockchaine corrupted!')

    print(f'Balance of {owner}: {get_balance(owner):.2f}')

print('Done!')
