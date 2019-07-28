from hash_util import hash_block, get_sha256


class Verification:

    def valid_proof(self, transactions, last_block_hash, proof, difficulty):
        '''Check amount of leading zerroes in hash
        Only after getting True inside this function
        new block will be added to the blockchain'''
        guess = str([tx.to_ordered_dict() for tx in transactions]) + str(last_block_hash) + str(proof)
        guess_hash = get_sha256(guess)
        print(guess_hash)
        return guess_hash.startswith(difficulty)

    def verify_chain(self, blockchain, difficulty):
        '''Verify each block['previous_block_hash'] vith calculated hash_block() of previous block'''
        for previous_block, block in enumerate(blockchain[1:]):
            # Verify previous block hash
            if block.previous_hash != hash_block(blockchain[previous_block]):
                print('Previous block hash is invalid')
                return False
            # Verify PoW of current block
            print('Verify chain > Validate PoW')
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.nonce, difficulty):
                print('Proof of Work is invalid')
                return False
        return True

    def verify_transaction(self, transaction, get_balance):
        '''Verify sender ability to do transaction
        If balance >= tx_amount
        '''
        sender_balance = get_balance(transaction.sender)
        return sender_balance >= transaction.amount

    def verify_transactions(self, open_transactions, get_balance):
        '''Verify ALL open transaction in pull'''
        # print([self.verify_transaction(tx, get_balance) for tx in open_transactions])
        return all([self.verify_transaction(tx, get_balance) for tx in open_transactions])
