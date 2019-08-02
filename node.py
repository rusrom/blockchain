from blockchain import Blockchain
from wallet import Wallet

from utility.verification import Verification


class Node:
    def __init__(self):
        self.wallet = Wallet()
        self.blockchain = Blockchain(self.wallet.address if self.wallet.public_key else None)

    def get_user_choice(self):
        print(
            '''----------------------------
            Choose what do you want to do?
                1: Send transaction
                2: Mine block
                3: Show blockchain
                4: Check transaction validity
                5: Show open transactions
                6: Create New Wallet
                7: Restore Existing Wallet
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
                # Check wallet address
                if not self.wallet.public_key:
                    print('Unavailable add transaction without wallet address. Please create or restore wallet!')
                    continue

                # Data for new transaction from user
                tx_recipient, tx_amount = self.get_transaction_value()

                # Sign transaction
                message_for_sign = self.wallet.address + tx_recipient + str(tx_amount)
                signature = self.wallet.sign_transaction(message_for_sign)

                # Adding new Transaction
                if self.blockchain.add_transaction(self.wallet.address, signature, tx_recipient, tx_amount):
                    print('Open transactions:', self.blockchain.get_open_transactions())
                else:
                    print('Transaction failed!')
            elif user_choice == '2':
                # Check wallet address
                if not self.wallet.public_key:
                    print('Unavailable mining without wallet address. Please create or restore wallet!')
                    continue

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
            elif user_choice == '6':
                # Create Wallet
                self.wallet.generate_keys()
                print('New Generated Address:', self.wallet.address)
                self.blockchain.hosting_node_id = self.wallet.address

                # Save keys private and public keys
                self.wallet.save_keys()
            elif user_choice == '7':
                # Restore Wallet
                try:
                    self.wallet.load_keys()
                except FileNotFoundError:
                    print('No key files detected! Key files in pem format must be inside key folder')
                    continue

                self.blockchain.hosting_node_id = self.wallet.address
            elif user_choice == 'q':
                break
            else:
                print('Your input is invalid')
                continue

            if not Verification.verify_chain(self.blockchain.get_chain(), self.blockchain.difficulty):
                raise Exception('[CRITICAL ERROR] Blockchaine corrupted!')

            if self.wallet.public_key:
                print(f'Balance of {self.wallet.address}: {self.blockchain.get_balance(self.wallet.address):.2f}')
            else:
                print('Warning, you have no wallet address')

        print('Exit the app.')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
