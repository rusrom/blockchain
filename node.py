from uuid import uuid4

from blockchain import Blockchain
# from verification import Verification
from utility.verification import Verification


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'rusrom'
        self.blockchain = Blockchain(self.id)

    def get_user_choice(self):
        print(
            '''----------------------------
            Choose what do you want to do?
                1: Send transaction
                2: Mine block
                3: Show blockchain
                4: Check transaction validity
                5: Show open transactions (pool)
                q: Quit
            ----------------------------''')
        return input('Your choice: ')

    def print_blockchain_elements(self):
        if not self.blockchain.get_chain():
            print('No blockchaine yet')
        else:
            for block in self.blockchain.get_chain():
                print(block)

    def print_open_transactions(self):
        if not self.blockchain.get_open_transactions():
            print('No open transactions yet')
        else:
            print('Open transactions:')
            for open_tx in self.blockchain.get_open_transactions():
                print(open_tx)

    def get_transaction_value(self):
        '''Returns the input of the user (transaction amount) as float'''
        tx_recipient = input('Enter the recipient of transaction: ')
        tx_amount = float(input('Enter transaction amount: '))
        return tx_recipient, tx_amount

    def listen_for_input(self):
        while True:
            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_recipient, tx_amount = self.get_transaction_value()
                if self.blockchain.add_transaction(self.id, tx_recipient, tx_amount):
                    print('Open transactions:', self.blockchain.get_open_transactions())
                else:
                    print('Transaction failed!')
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if self.blockchain.get_open_transactions():
                    if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_sender_balance, self.blockchain.get_sender_transactions_coins):
                        print('All transactions are valid')
                    else:
                        print('[ERROR] There are invalid open transactions in pull')
                else:
                    print('No one open transaction yet')
            elif user_choice == '5':
                self.print_open_transactions()
            elif user_choice == 'q':
                break
            else:
                print('Your input is invalid')
                continue

            if not Verification.verify_chain(self.blockchain.get_chain(), self.blockchain.difficulty):
                raise Exception('[CRITICAL ERROR] Blockchaine corrupted!')

            print(f'Balance of {self.id}: {self.blockchain.get_balance(self.id):.2f}')

        print('Done!')


node = Node()
node.listen_for_input()
