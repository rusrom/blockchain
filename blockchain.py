MINING_REWARD = 10
blockchain = []
open_transactions = []
owner = 'rusrom'
participants = set()


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


def add_transaction(recipient, amount, sender=owner):
    '''Append a new value as well as the last blockchain value to the blockchain
    Like adding transaction to the pool in real life
    Arguments:
        :recipient: The recipient of the coins
        :amount: The amount of coins that should be sent
        :sender: The sender(default=owner) of the coins
    '''
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }

    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def hash_block(previous_block):
    return ''.join([str(val) for val in previous_block.values()])


def get_balance(participant):
    tx_inputs = [
        tx['amount']
        for block in blockchain for tx in block['transactions']
        if tx['recipient'] == participant
    ]

    tx_outputs = [
        tx['amount']
        for block in blockchain for tx in block['transactions']
        if tx['sender'] == participant
    ]

    # All sending transactions in open_transactions(pool)
    tx_open = [
        tx['amount']
        for tx in open_transactions
        if tx['sender'] == participant
    ]

    return sum(tx_inputs) - sum(tx_outputs) - sum(tx_open)


def mine_block():
    # Candy for miner
    reward_transaction = {
        'sender': 'MINING_REWARD_BOT',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    open_transactions.append(reward_transaction)

    if blockchain:
        previous_block = blockchain[-1]
        previous_block_hash = hash_block(previous_block)

        block = {
            'previous_block_hash': previous_block_hash,
            'index': len(blockchain),
            'transactions': open_transactions[:],
        }
    else:
        block = {
            'previous_block_hash': 'Genesis Block',
            'index': 0,
            'transactions': open_transactions[:],
        }
    blockchain.append(block)
    open_transactions.clear()


def get_user_choice():
    print(
        '''----------------------------
        Choose what do you want to do?
            1: Send transaction
            2: Mine block
            3: Show blockchain
            4: Show participants
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
    for previous_block, block in enumerate(blockchain[1:]):
        if block['previous_block_hash'] != hash_block(blockchain[previous_block]):
            return False
    return True


def show_participants():
    print(participants)


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

    print('Balance:', get_balance('rusrom'))

print('Done!')
