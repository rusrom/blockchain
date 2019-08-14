import json

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_wallet():
    response = wallet.generate_keys()
    response['balance'] = blockchain.get_balance(wallet.address)
    wallet.save_keys()
    blockchain.hosting_node_id = wallet.address
    blockchain.hosting_node_public_key = wallet.public_key
    return jsonify(response), 200


@app.route('/wallet', methods=['GET'])
def load_wallet():
    response = wallet.load_keys()
    response['balance'] = blockchain.get_balance(wallet.address)
    blockchain.hosting_node_id = wallet.address
    blockchain.hosting_node_public_key = wallet.public_key
    return jsonify(response), 200


@app.route('/balance', methods=['GET'])
def get_balance():
    response = {
        'wallet': wallet.public_key is not None
    }

    if response['wallet']:
        response['message'] = f'Balance for {wallet.address}'
        response['balance'] = blockchain.get_balance(wallet.address)
        status_code = 200
    else:
        response['message'] = 'Create or restore wallet'
        response['balance'] = None
        status_code = 501

    return jsonify(response), status_code


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    '''Return result of adding broadcast transaction on remote peer node
    as descriptive message with appropriate status code.
    Result catched by brodcasting node with blockchain.broadcast_to_other_nodes() method
    '''
    status_code = 400
    response = {'message': 'No data found in request'}

    transaction = json.loads(request.json)
    if transaction:
        required_fields = ['sender', 'public_key', 'signature', 'recipient', 'amount']
        if all([field in required_fields for field in transaction]):
            result = blockchain.add_transaction(
                sender=transaction['sender'],
                public_key=transaction['public_key'],
                signature=transaction['signature'],
                recipient=transaction['recipient'],
                amount=transaction['amount'],
                broadcast=False
            )
            if result['transaction']:
                status_code = 200
            response['message'] = result['message']
        else:
            response['message'] = 'Missing required field(s)'

    return jsonify(response), status_code


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    status_code = 500
    response = {}

    # Check configured remote nodes
    if blockchain.nodes:
        result = blockchain.resolve()
        if result:
            status_code = 200
            response['message'] = 'Blackchain was successfuly updated'
        else:
            response['message'] = 'Error during Blackchain update'
    else:
        response['message'] = 'No configured network nodes'

    return jsonify(response), status_code


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    response = {
        'block': False
    }

    # Get block data as a dict
    broadcast_block = json.loads(request.json)

    # Check request has data
    if not broadcast_block:
        response['message'] = 'No data found in request'
        return jsonify(response), 400

    # Check block was mined by broadcsting node
    if not broadcast_block.get('nonce'):
        response['message'] = 'Block was not mined on broadcasting node'
        return jsonify(response), 400

    # Check last block index in blockchain of current node with recieved broadcast block index
    if broadcast_block['index'] == blockchain.get_chain()[-1].index + 1:
        # index of boadcast block is equal of next index in current node blockchain
        # current node and broadcasting node has UPTODATE STATE
        # TODO: Get message that return blockchain.add_block() and add it to response['message']
        if blockchain.add_block(broadcast_block):
            response['block'] = True
            response['message'] = 'BROADCAST BLOCK WAS ADDED'
            return jsonify(response), 200
        # Broadcasted block was not excepted by current node
        response['message'] = 'BROADCAST BLOCK ADDING WAS FAILED'
        return jsonify(response), 400
    elif broadcast_block['index'] > blockchain.get_chain()[-1].index + 1:
        # index of boadcast block is greater then next index in current node blockchain
        # Recieving current node blockchain has OLDER STATE
        response['message'] = 'Block didnt add! Broadcast blockchain seems to be LONGER STATE'
        print('Block didnt add! Broadcast blockchain seems to be LONGER STATE')
        # RESOLVE ON RECIEVING SIDE: Blockchain is not in SYNC! Need update blockchain to longest one
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        # next block index of current node blockchain is greater then boadcast block index
        # broadcast node blockchain is OLDER STATE
        response['message'] = 'Your blockchain has SHORTER CHAIN then other nodes'
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():
    '''Add new transaction'''
    status_code = 501
    response = {
        'transaction': False,
    }

    if not wallet.public_key:
        response['message'] = 'Create or restore wallet'
        return jsonify(response), status_code

    response['balance'] = blockchain.get_balance(wallet.address)

    request_data = request.get_json()
    if request_data:
        required_fields = ['recipient', 'amount']
        if all([field in required_fields for field in request_data]):
            recipient = request_data['recipient']
            amount = request_data['amount']

            # Sign transaction
            message = wallet.address + recipient + str(amount)
            signature = wallet.sign_transaction(message)

            # Add transaction
            result = blockchain.add_transaction(wallet.address, wallet.public_key_to_string(), signature, recipient, amount)
            if result['transaction']:
                response['message'] = result['message']
                response['transaction'] = result['transaction']
                response['balance'] = blockchain.get_balance(wallet.address)
                status_code = 200
            else:
                response['message'] = result['message']
                response['balance'] = blockchain.get_balance(wallet.address)
        else:
            response['message'] = 'Required fields missing'
    else:
        response['message'] = 'No data found inside incoming request'

    return jsonify(response), status_code


@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain_dict), 200


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    open_transactions = blockchain.open_transactions_as_dict()
    return jsonify(open_transactions), 200


@app.route('/mine', methods=['POST'])
def mine():
    # Check blockchain SYNC: Need update blockchain to lobgest one?
    if blockchain.resolve_conflicts:
        response = {'message': 'Resolve conflict. Node blockchain is not in sync with network'}
        return jsonify(response), 409

    status_code = 501
    response = blockchain.mine_block()
    if response['block']:
        status_code = 200
    response['balance'] = blockchain.get_balance(blockchain.hosting_node_id)
    return jsonify(response), status_code


@app.route('/nodes', methods=['GET'])
def get_nodes():
    code_response = 200
    response = {
        'all_nodes': blockchain.nodes
    }
    if response['all_nodes']:
        response['message'] = f'You added {len(response["all_nodes"])} node(s)'
    else:
        code_response = 501
        response['message'] = 'You did\'t add any node yet'
    return jsonify(response), code_response


@app.route('/node', methods=['POST'])
def add_node():
    status_code = 501
    response = {
        'all_nodes': None,
    }
    values = request.get_json()
    if values and 'node' in values:
        node = values['node']
        blockchain.add_peer_node(node)

        status_code = 200
        response['message'] = 'Node was added'
        response['all_nodes'] = blockchain.nodes
    else:
        response['message'] = 'No data with node attached'

    return jsonify(response), status_code


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    status_code = 400
    response = {
        'message': 'No such node found',
        'all_nodes': blockchain.nodes
    }
    if node_url:
        blockchain.remove_peer_node(node_url)
        status_code = 200
        response['message'] = f'Node {node_url} removed from list of nodes'
        response['all_nodes'] = blockchain.nodes

    return jsonify(response), status_code

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port

    blockchain = Blockchain(port)
    wallet = Wallet(port)

    app.run(host='127.0.0.1', port=port)
