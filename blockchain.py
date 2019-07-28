import json
import pickle
# from hashlib import sha256

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification


MINING_REWARD = 10
DIFFICULTY = '0' * 2


# verifier = Verification()


class Blockchain:
    def __init__(self, hosting_node_id):
        self.hosting_node_id = hosting_node_id
        self.open_transactions = []
        self.genesis_block = Block(
            index=0,
            previous_hash='Genesis_Block',
            transactions=self.open_transactions[:],
            nonce=0
        )
        self.chain = [self.genesis_block]
        self.load_data()
        self.verifier = Verification()
        self.difficulty = DIFFICULTY

    def load_data(self):
        try:
            with open('blockchain.txt') as f:
                file_content = f.readlines()
        except FileNotFoundError:
            print('Genesis block innit...')
            return

        # Read data from dump file and convert them to right format
        # List of Block Classes with transactions as list of Transaction Classes
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
                    for tx in block_dump['transactions']
                ],
                nonce=block_dump['nonce'],
                timestamp=block_dump['timestamp']
            )
            corrected_blockchain_dump.append(block)
        self.chain = corrected_blockchain_dump[:]

        self.open_transactions = [
            Transaction(
                sender=tx['sender'],
                recipient=tx['recipient'],
                amount=tx['amount']
            )
            for tx in json.loads(file_content[1])
        ]

    def save_data(self):
        blockchain_blocks_to_dict = [block.__dict__.copy() for block in self.chain]

        for block in blockchain_blocks_to_dict:
            transactions_to_dict = [tx.to_ordered_dict() for tx in block['transactions']]
            block['transactions'] = transactions_to_dict

        open_transactions_to_dict = [tx.__dict__.copy() for tx in self.open_transactions]

        with open('blockchain.txt', 'w') as f:
            f.write(json.dumps(blockchain_blocks_to_dict) + '\n')
            f.write(json.dumps(open_transactions_to_dict))

    def load_data_pickle(self):
        try:
            with open('blockchain.p', 'rb') as f:
                file_content = pickle.loads(f.read())
            self.chain = file_content['blockchain']
            self.open_transactions = file_content['open_transactions']
        except FileNotFoundError:
            print('Genesis block innit...')

    def save_data_pickle(self):
        save_data = {
            'blockchain': self.chain,
            'open_transactions': self.open_transactions
        }
        with open('blockchain.p', 'wb') as f:
            f.write(pickle.dumps(save_data))

    def proof_of_work(self):
        '''Struggle with DIFFICULTY seeking correct proof'''
        last_block = self.chain[-1]
        last_block_hash = hash_block(last_block)

        nonce = 0
        while not self.verifier.valid_proof(self.open_transactions, last_block_hash, nonce, DIFFICULTY):
            nonce += 1
        return nonce

    def get_balance(self, participant):
        '''Get balance of participant coins
        Input amount - Outpu amount - Amount of coins in open transaction (in pull)
        '''
        tx_inputs = [
            tx.amount
            for block in self.chain
            for tx in block.transactions
            if tx.recipient == participant
        ]

        tx_outputs = [
            tx.amount
            for block in self.chain
            for tx in block.transactions
            if tx.sender == participant
        ]

        # Participant's All sending transactions that are in open_transactions(pool)
        tx_open = [
            tx.amount
            for tx in self.open_transactions
            if tx.sender == participant
        ]

        return sum(tx_inputs) - sum(tx_outputs) - sum(tx_open)

    def get_sender_balance(self, participant):
        '''Get balance of participant'''
        tx_inputs = [
            tx.amount
            for block in self.chain
            for tx in block.transactions
            if tx.recipient == participant
        ]

        tx_outputs = [
            tx.amount
            for block in self.chain
            for tx in block.transactions
            if tx.sender == participant
        ]

        return sum(tx_inputs) - sum(tx_outputs)

    def get_sender_transactions_coins(self, participant):
        '''Get participant coins in transactions'''
        amounts_open_txs = [
            tx.amount
            for tx in self.open_transactions
            if tx.sender == participant
        ]
        return sum(amounts_open_txs)

    def get_last_blockchain_value(self):
        '''Returns the last value of current blockchain'''
        if self.chain:
            return self.chain[-1]
        return None

    def add_transaction(self, sender, recipient, amount):
        '''Add transaction to th open transactions list
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

        if self.verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        # Reward transaction for miners
        reward_transaction = Transaction(
            sender='MINING_REWARD_BOT',
            recipient=self.hosting_node_id,
            amount=MINING_REWARD
        )

        # IMPORTANT: Proof of Work should NOT INCLUDE REWARD TRANSACTION
        nonce = self.proof_of_work()

        # Add reward transaction
        self.open_transactions.append(reward_transaction)

        # Create block
        block = Block(
            index=len(self.chain),
            previous_hash=hash_block(self.chain[-1]),
            transactions=self.open_transactions[:],
            nonce=nonce
        )

        # Add block to blockchain
        self.chain.append(block)

        # Clear open transactions
        self.open_transactions.clear()

        # Dump blockchain and open transactions to file
        self.save_data()
