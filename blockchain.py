blockchain = []


def get_last_blockchain_value():
    '''Returns the last value of current blockchain'''
    if blockchain:
        return blockchain[-1]


def add_transaction(transaction_amount):
    '''Append a new value as well as the last blockchain value to the blockchain
    Arguments:
        :transaction_amount: The amount of cryptocurrency that should be sent
    '''
    if blockchain:
        previous_bloocks = get_last_blockchain_value()
        blockchain.append([previous_bloocks, transaction_amount])
    else:
        # Genesis block
        blockchain.append([transaction_amount])


def get_user_choice():
    print(
        '''
----------------------------
Choose what do you want to do?
    1: Send transaction
    2: Show blockchain
    h: Manipulate the blockchaine
    q: Quit
----------------------------
        '''
    )
    return input('Your choice: ')


def get_transaction_value():
    '''Returns the input of the user (transaction amount) as float'''
    return float(input('Your tranaction amount please: '))


def print_blockchain_elements():
    if not blockchain:
        print('No blockchaine yet')
    else:
        for block in blockchain:
            print(block)


def verify_chain():
    is_valid = True
    for previous_block, block in enumerate(blockchain[1:]):
        if block[0] != blockchain[previous_block]:
            is_valid = False
            break
    return is_valid


while True:
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_amount = get_transaction_value()
        add_transaction(tx_amount)
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == 'q':
        break
    elif user_choice == 'h':
        if blockchain:
            blockchain[0] = [100.0]
            print('BOOM')
        else:
            print('No blockchaine yet')
    else:
        print('Your input is invalid')
        continue

    if not verify_chain():
        raise Exception('[CRITICAL ERROR] Blockchaine corrupted!')

    print('Choice was registered')

print('Done!')
