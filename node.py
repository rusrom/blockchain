from flask import Flask
from flask_cors import CORS

from wallet import Wallet


app = Flask(__name__)
CORS(app)

wallet = Wallet()


@app.route('/', methods=['GET'])
def ui():
    return 'It Works!'

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
