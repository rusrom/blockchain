## Blockchain and Cryptocurrency using Python3 and cryptography package  
<a href="http://www.youtube.com/watch?v=C7agcjpeWfo"><img src="https://blogs.iadb.org/caribbean-dev-trends/wp-content/uploads/sites/34/2017/12/Blockchain1.jpg" alt="Blockchain in Python 3" width="100%" /></a>

``cryptography`` is a package which provides cryptographic recipes and primitives to Python developers.  

How a Blockchain works?    
It's an exciting project that help to understand what Blockchain really is.  

Some issues that was developed:  
- Generate, store and load private and public keys
- Private key optionaly encrypted while saving as file using a password
- Use SHA256 for wallet addresses
- Sign transaction using private key
- Check transaction signature using public key
- Get balance using input/output/open transactions
- Check balance before sending transaction
- Genesis Block
- Difficulty of mining (numbers of leading zeroes)
- Mining reward
- Previous block hash check
- Check Proof of Work using block nonce, transactions(excluding reward transaction), previous hash
- Adding peer nodes
- Broadcast transaction to other peer nodes
- Broadcast block to to other peer nodes
- Consensus - longest chain wins
- Check blockchain length on node start
- Prevent sending transaction if node Blockchain is short
- Prevent mining block if node Blockchain is short
- Don't accept any broadcast if node Blockchain is short
- Update to longest Blockchain from configured peer nodes
