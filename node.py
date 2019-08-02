from flask import Flask, jsonify
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
wallet = Wallet()


@app.route('/', methods=['GET'])
def ui():
    return 'It Works!'


@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain_dict)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
