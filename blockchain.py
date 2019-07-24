blockchain = []


def get_last_blockchain_value():
    if len(blockchain):
        return blockchain[-1]
    return None


def add_value(transaction_amount):
    if blockchain:
        blockchain.append([get_last_blockchain_value(), transaction_amount])
    else:
        blockchain.append([transaction_amount])


def get_user_input():
    return float(input('Your tranaction amount please: '))

add_value(get_user_input())
add_value(get_user_input())
add_value(get_user_input())
add_value(get_user_input())

# for block in blockchain:
#     print(block)

print(blockchain)
