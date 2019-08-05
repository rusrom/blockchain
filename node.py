from flask import Flask, jsonify
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
wallet = Wallet()


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
    else:
        response['message'] = 'Create or restore wallet'
        response['balance'] = None
    return jsonify(response), 200


@app.route('/', methods=['GET'])
def ui():
    return 'It Works!'


@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain_dict)


@app.route('/mine', methods=['POST'])
def mine():
    response = blockchain.mine_block()
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
