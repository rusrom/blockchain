from collections import OrderedDict
from hashlib import sha256

from hash_util import hash_block

MINING_REWARD = 10
DIFFICULTY = '00'

blockchain = []
open_transactions = []
owner = 'rusrom'
participants = {owner}


def get_last_blockchain_value():
    '''Returns the last value of current blockchain'''
    if blockchain:
        return blockchain[-1]


def verify_transaction(transaction):
    '''Verify sender ability to do transaction
    If balance >= tx_amount
    '''
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    '''Verify ALL open transaction in pull
    '''
    return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(recipient, amount, sender=owner):
    '''Append a new value as well as the last blockchain value to the blockchain
    Like adding transaction to the pool in real life
    Arguments:
        :recipient: The recipient of the coins
        :amount: The amount of coins that should be sent
        :sender: The sender(default=owner) of the coins
    '''
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = OrderedDict([
        ('sender', sender),
        ('recipient', recipient),
        ('amount', amount)
    ])

    if verify_transaction(transaction):
        # Add to pull
        open_transactions.append(transaction)

        # Add unique participant to set of all participants of blockchain
        participants.add(sender)
        participants.add(recipient)

        return True
    return False


def valid_proof(transactions, last_block_hash, proof):
    '''Check amount of leading zerroes in hash'''
    guess = (str(transactions) + str(last_block_hash) + str(proof)).encode()
    guess_hash = sha256(guess).hexdigest()
    print('valid_proof() >>>', guess_hash)
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
    # Candy for miner
    # reward_transaction = {
    #     'sender': 'MINING_REWARD_BOT',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict([
        ('sender', 'MINING_REWARD_BOT'),
        ('recipient', owner),
        ('amount', MINING_REWARD)
    ])

    # IMPORTANT: Proof of Work should NOT INCLUDE REWARD TRANSACTION
    if blockchain:
        proof = proof_of_work()

    # Add reward transaction
    open_transactions.append(reward_transaction)

    if blockchain:
        previous_block = blockchain[-1]
        previous_block_hash = hash_block(previous_block)

        block = {
            'previous_block_hash': previous_block_hash,
            'index': len(blockchain),
            'transactions': open_transactions[:],
            'proof': proof,
        }
    else:
        block = {
            'previous_block_hash': 'Genesis Block',
            'index': 0,
            'transactions': open_transactions[:],
            'proof': 100,
        }
    blockchain.append(block)
    open_transactions.clear()


def get_balance(participant):
    '''Get balance of participant coins
    Input amount - Outpu amount - Amount of coins in open transaction (in pull)
    '''
    tx_inputs = [
        tx['amount']
        for block in blockchain
        for tx in block['transactions']
        if tx['recipient'] == participant
    ]

    tx_outputs = [
        tx['amount']
        for block in blockchain
        for tx in block['transactions']
        if tx['sender'] == participant
    ]

    # Participant's All sending transactions that are in open_transactions(pool)
    tx_open = [
        tx['amount']
        for tx in open_transactions
        if tx['sender'] == participant
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
            h: Hack blockchaine
            q: Quit
        ----------------------------''')
    return input('Your choice: ')


def get_transaction_value():
    '''Returns the input of the user (transaction amount) as float'''
    tx_recipient = input('Enter the recipient of transaction: ')
    tx_amount = float(input('Enter tranaction amount: '))
    return tx_recipient, tx_amount


def print_blockchain_elements():
    if not blockchain:
        print('No blockchaine yet')
    else:
        for block in blockchain:
            print(block)


def verify_chain():
    '''Verify each block['previous_block_hash'] vith calculated hash_block() of previous block'''
    for previous_block, block in enumerate(blockchain[1:]):
        # Verify previous block hash
        if block['previous_block_hash'] != hash_block(blockchain[previous_block]):
            return False
        # Verify PoW of current block
        print('195 Verify chain')
        if not valid_proof(block['transactions'][:-1], block['previous_block_hash'], block['proof']):
            print('Proof of Work is invalid')
            return False
    return True


def show_participants():
    print(participants)


def show_participants_balances():
    '''Show balaces for all participants of blockchain'''
    for participant in participants:
        print(f'{participant}: {get_balance(participant)} coins')


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
    elif user_choice == 'q':
        break
    elif user_choice == 'h':
        if blockchain:
            blockchain[0] = {
                'previous_block_hash': '232523542b2j3r2j3rbj234rbj243hrbj2',
                'index': 8,
                'transactions': [{'sender': 'rusrom', 'recipient': 'korova', 'amount': 1_000_000_000_000}],
            }
            print('BOOM')
        else:
            print('No blockchaine yet')
    else:
        print('Your input is invalid')
        continue

    if not verify_chain():
        raise Exception('[CRITICAL ERROR] Blockchaine corrupted!')

    print(f'Balance of {owner}: {get_balance(owner):.2f}')

print('Done!')
