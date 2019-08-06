from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
wallet = Wallet()


@app.route('/', methods=['GET'])
def ui():
    return send_from_directory('ui', 'node.html')


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
    open_transactions = blockchain.open_transaction_as_dict()
    return jsonify(open_transactions), 200


@app.route('/mine', methods=['POST'])
def mine():
    status_code = 501
    response = blockchain.mine_block()
    if response['block']:
        # return jsonify(response), 200
        status_code = 200
    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
