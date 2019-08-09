import json
import pickle
import requests
# from hashlib import sha256

# from hash_util import hash_block
from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
# from verification import Verification
from utility.verification import Verification

from wallet import Wallet


MINING_REWARD = 10
DIFFICULTY = '0' * 2


# verifier = Verification()


class Blockchain:
    def __init__(self, hosting_node_port):
        self.hosting_node_id = None
        self.hosting_node_public_key = None
        self.hosting_node_port = hosting_node_port
        self.__open_transactions = []
        self.genesis_block = Block(
            index=0,
            previous_hash='Genesis_Block',
            transactions=self.__open_transactions[:],
            nonce=0
        )
        self.__chain = [self.genesis_block]
        self.__peer_nodes = set()
        self.load_data()
        self.difficulty = DIFFICULTY

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_blockchain(self):
        # Read data from dump file
        try:
            with open(f'data/blockchain/{self.hosting_node_port}-blockchain.txt') as f:
                file_content = f.read()
        except FileNotFoundError:
            print('Genesis block innit...')
            return

        # Convert file content to right format
        corrected_blockchain_dump = []

        # Iterate through all blocks(dict) in list and transform them from dict to Block Objects
        for block_dump in json.loads(file_content):
            block = Block(
                index=block_dump['index'],
                previous_hash=block_dump['previous_hash'],
                # All transactions from dict to Transaction Class
                transactions=[
                    Transaction(
                        sender=tx['sender'],
                        public_key=tx['public_key'],
                        signature=tx['signature'],
                        recipient=tx['recipient'],
                        amount=tx['amount']
                    )
                    for tx in block_dump['transactions']
                ],
                nonce=block_dump['nonce'],
                timestamp=block_dump['timestamp']
            )
            corrected_blockchain_dump.append(block)
        self.__chain = corrected_blockchain_dump[:]

    def load_transactions(self):
        try:
            with open(f'data/transactions/{self.hosting_node_port}-open-transactions.txt') as f:
                file_content = f.read()
        except FileNotFoundError:
            print('Genesis block innit...')
            return

        self.__open_transactions = [
            Transaction(
                sender=tx['sender'],
                public_key=tx['public_key'],
                signature=tx['signature'],
                recipient=tx['recipient'],
                amount=tx['amount']
            )
            for tx in json.loads(file_content)
        ]

    def load_data(self):
        self.load_blockchain()
        self.load_transactions()
        self.load_peer_nodes()
        return 'ok'

    @property
    def chain_dict(self):
        # Convert list of Block Classes to list of dicts
        blockchain_blocks_to_dict = [block.__dict__.copy() for block in self.__chain]

        # Convert block transactions from Transaction Classes to dicts
        for block in blockchain_blocks_to_dict:
            block['transactions'] = [tx.__dict__ for tx in block['transactions']]

        return blockchain_blocks_to_dict

    def block_as_dict(self, block):
        # Convert Block Object to dictionary
        block_dict = block.__dict__.copy()
        # Convert block transactions from Transaction Objects to dictionaries
        block_dict['transactions'] = [tx.__dict__.copy() for tx in block_dict['transactions']]
        return block_dict

    def open_transactions_as_dict(self):
        # Convert list of open transactions from Transaction Classes to dicts
        return [tx.__dict__.copy() for tx in self.__open_transactions]

    def block_as_object(self, block_dict):
        block = Block(
            index=block_dict['index'],
            previous_hash=block_dict['previous_hash'],
            # All transactions from dict to Transaction Class
            transactions=[
                Transaction(
                    sender=tx['sender'],
                    public_key=tx['public_key'],
                    signature=tx['signature'],
                    recipient=tx['recipient'],
                    amount=tx['amount']
                )
                for tx in block_dict['transactions']
            ],
            nonce=block_dict['nonce'],
            timestamp=block_dict['timestamp']
        )
        return block

    def save_blockchain(self):
        # Convert list of Block Classes to list of dicts
        blockchain_blocks_to_dict = [block.__dict__.copy() for block in self.__chain]

        # Convert block transactions from Transaction Objects to dicts
        for block in blockchain_blocks_to_dict:
            block['transactions'] = [tx.to_ordered_dict() for tx in block['transactions']]

        with open(f'data/blockchain/{self.hosting_node_port}-blockchain.txt', 'w') as f:
            f.write(json.dumps(blockchain_blocks_to_dict))

    def save_open_transactions(self):
        # Convert open transactions list of Transaction Objects to list of dicts
        open_transactions_to_dict = [tx.__dict__.copy() for tx in self.__open_transactions]
        with open(f'data/transactions/{self.hosting_node_port}-open-transactions.txt', 'w') as f:
            f.write(json.dumps(open_transactions_to_dict))

    # def load_data_pickle(self):
    #     try:
    #         with open(f'dump/{self.hosting_node_port}-blockchain.p', 'rb') as f:
    #             file_content = pickle.loads(f.read())
    #         self.__chain = file_content['blockchain']
    #         self.__open_transactions = file_content['open_transactions']
    #     except FileNotFoundError:
    #         print('Genesis block innit...')

    # def save_data_pickle(self):
    #     save_data = {
    #         'blockchain': self.__chain,
    #         'open_transactions': self.__open_transactions
    #     }
    #     with open(f'dump/{self.hosting_node_port}-blockchain.p', 'wb') as f:
    #         f.write(pickle.dumps(save_data))

    def proof_of_work(self):
        '''Struggle with DIFFICULTY seeking correct proof'''
        last_block = self.__chain[-1]
        last_block_hash = hash_block(last_block)

        nonce = 0
        while not Verification.valid_proof(self.__open_transactions, last_block_hash, nonce, DIFFICULTY):
            nonce += 1
        return nonce

    def get_balance(self, participant):
        '''Get balance of participant coins
        Input amount - Outpu amount - Amount of coins in open transaction (in pull)
        '''
        tx_inputs = [
            tx.amount
            for block in self.__chain
            for tx in block.transactions
            if tx.recipient == participant
        ]

        tx_outputs = [
            tx.amount
            for block in self.__chain
            for tx in block.transactions
            if tx.sender == participant
        ]

        # Participant's All sending transactions that are in open_transactions(pool)
        tx_open = [
            tx.amount
            for tx in self.__open_transactions
            if tx.sender == participant
        ]

        return sum(tx_inputs) - sum(tx_outputs) - sum(tx_open)

    def get_sender_balance(self, participant):
        '''Get balance of participant'''
        tx_inputs = [
            tx.amount
            for block in self.__chain
            for tx in block.transactions
            if tx.recipient == participant
        ]

        tx_outputs = [
            tx.amount
            for block in self.__chain
            for tx in block.transactions
            if tx.sender == participant
        ]

        return sum(tx_inputs) - sum(tx_outputs)

    def get_sender_transactions_coins(self, participant):
        '''Get participant coins in transactions'''
        amounts_open_txs = [
            tx.amount
            for tx in self.__open_transactions
            if tx.sender == participant
        ]
        return sum(amounts_open_txs)

    def get_last_blockchain_value(self):
        '''Returns the last value of current blockchain'''
        if self.__chain:
            return self.__chain[-1]
        return None

    def add_transaction(self, sender, public_key, signature, recipient, amount, broadcast=True):
        '''Add transaction to th open transactions list
        Arguments:
            :sender: sender wallet address
            :public_key: sender public key
            :signature: signed transaction message
            :recipient: The recipient of the coins
            :amount: The amount of coins that should be sent
        '''

        # Check wallet address
        if not self.hosting_node_id:
            print('Adding transactions without wallet address blocked. Please create or restore wallet!')
            return False

        transaction = Transaction(
            sender=sender,
            public_key=public_key,
            signature=signature,
            recipient=recipient,
            amount=amount
        )

        # Check sender balance before accepting transacion
        if not Verification.verify_transaction(transaction, self.get_balance):
            print('Sender balance is not enough for transaction')
            return False

        # Add transaction to open transactions on current node
        self.__open_transactions.append(transaction)

        # Save open transactions to file on current node
        self.save_open_transactions()

        transaction_as_dict = transaction.__dict__.copy()

        # Broadcast transaction to other nodes only if current node adding it
        if broadcast:
            for node in self.__peer_nodes:
                node_url = f'http://{node}/broadcast-transaction'
                try:
                    response = requests.post(node_url, json=json.dumps(transaction_as_dict))
                    if response.ok:
                        print(f'Transaction accepted by {node}')
                    else:
                        print(f'{node}: Transaction declined, needs resolving')
                        continue
                except requests.exceptions.ConnectionError:
                    print(f'{node}: Connection error')
                    continue
            print('Transaction saved on current node and broadcasted on other.')
        return transaction_as_dict

    def mine_block(self):
        response = {
            'block': False,
            'wallet': self.hosting_node_id is not None,
            'balance': None
        }

        # Check wallet address. We can't mine without wallet address. We need get mining reward
        if not self.hosting_node_id:
            # print('Can\'t mine without wallet address. Please create or restore wallet!')
            response['message'] = 'Create or restore wallet'
            return response

        # Check signatures opened transactions before adding to block
        for tx in self.__open_transactions:
            message = tx.sender + tx.recipient + str(tx.amount)
            if not Wallet.check_signature(tx.public_key, message, tx.signature):
                # print(f'Transaction to {tx.recipient} with amount: {tx.amount} has bad signature! Block not be mine')
                response['message'] = f'Transaction to {tx.recipient} has bad signature'
                response['balance'] = self.get_balance(self.hosting_node_id)
                return response

        # Reward transaction for miners
        reward_transaction = Transaction(
            sender='MINING_REWARD_BOT',
            public_key='MINING_REWARD_BOT_PUBLIC_KEY',
            signature='MINING_REWARD_BOT_SIGNATURE',
            recipient=self.hosting_node_id,
            amount=MINING_REWARD
        )

        # IMPORTANT: Proof of Work should NOT INCLUDE REWARD TRANSACTION
        nonce = self.proof_of_work()

        # Add reward transaction
        self.__open_transactions.append(reward_transaction)

        # Create block
        block = Block(
            index=len(self.__chain),
            previous_hash=hash_block(self.__chain[-1]),
            transactions=self.__open_transactions[:],
            nonce=nonce
        )

        # Add block to blockchain
        self.__chain.append(block)

        # Clear open transactions
        self.__open_transactions.clear()

        # Save blockchain to file after mining block
        self.save_blockchain()

        # Save transactions to file after mining block
        self.save_open_transactions()

        response['block'] = self.block_as_dict(block)
        response['message'] = f'Block successfuly added to blockchain'
        response['balance'] = self.get_balance(self.hosting_node_id)
        return response

    def add_block(self, broadcsast_block):
        '''Add block to blockchain after broadcast request'''
        block = self.block_as_object(broadcsast_block)

        # Check Proof of Work of broadcating block
        is_valid_pow = Verification.valid_proof(block.transactions, block.previous_hash, block.nonce, DIFFICULTY)
        if not is_valid_pow:
            print('Error in Proof of Work of broadcating block')
            return False

        # Check previous block hashes of current node and broadcasted block
        is_hashes_match = hash_block(self.__chain[-1]) == block.previous_hash
        if not is_hashes_match:
            print('Error in previous block hashes of recieving node and broadcasted block')
            return False

        # Add broadcasted block to current node blockchain
        self.__chain.append(block)
        print('Broadcasted block was added to current node blockchain')

        # Save blockchain to file after adding broadcasted block
        self.save_blockchain()

        return True

    def save_peer_nodes(self):
        peer_nodes_list = list(self.__peer_nodes)
        peer_nodes_string = json.dumps(peer_nodes_list)
        with open(f'data/broadcast/{self.hosting_node_port}-peer-nodes.txt', 'w') as f:
            f.write(peer_nodes_string)

    def load_peer_nodes(self):
        try:
            with open(f'data/broadcast/{self.hosting_node_port}-peer-nodes.txt') as f:
                peer_nodes_string = f.read()
        except FileNotFoundError:
            print('No dump file with nodes')
            return False
        peers_list = json.loads(peer_nodes_string)
        self.__peer_nodes = set(peers_list)

    def add_peer_node(self, node):
        '''Add a new node to the peer node set
        Arguments:
            :node: The node URL which should be added'''
        self.__peer_nodes.add(node)
        self.save_peer_nodes()

    def remove_peer_node(self, node):
        '''Remove node from the peer node set
        Arguments:
            :node: The node URL which should be removed'''
        self.__peer_nodes.discard(node)
        self.save_peer_nodes()

    @property
    def nodes(self):
        '''Return a list of all connected nodes'''
        return list(self.__peer_nodes)
