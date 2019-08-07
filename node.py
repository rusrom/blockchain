from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
CORS(app)

# blockchain = Blockchain()
# wallet = Wallet()


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
    status_code = 400
    response = {
        'message': 'No data found in request',
        'transaction': False
    }
    transaction = request.get_json()
    if transaction:
        required_fields = ['sender', 'signature', 'recipient', 'amount']

        if all([field in required_fields for field in transaction]):
            result = blockchain.add_transaction(
                sender=transaction['sender'],
                signature=transaction['signature'],
                recipient=transaction['recipient'],
                amount=transaction['amount']
            )
            if result:
                response['message'] = 'Successfuly added transaction'
                response['transaction'] = transaction
                status_code = 200
            else:
                response['message'] = f'Transaction was not accepted by {blockchain.hosting_node_port}'
                status_code = 500
        else:
            response['message'] = 'Missing required field(s)'

    return jsonify(response), status_code


@app.route('/transaction', methods=['POST'])
def add_transaction():
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
            transaction = blockchain.add_transaction(wallet.address, signature, recipient, amount)
            if transaction:
                response['message'] = 'Successfuly added transaction'
                response['transaction'] = transaction
                response['balance'] = blockchain.get_balance(wallet.address)
                status_code = 200
            else:
                response['message'] = 'Creating transaction faild'
                response['balance'] = blockchain.get_balance(wallet.address)
        else:
            response['message'] = 'Required fields missing'
    else:
        response['message'] = 'No data found inside incoming request'

    # if response['transaction']:
    #     return jsonify(response), 200
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
    status_code = 501
    response = blockchain.mine_block()
    if response['block']:
        # return jsonify(response), 200
        status_code = 200
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
