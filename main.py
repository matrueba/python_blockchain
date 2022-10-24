from flask import Flask, jsonify, request
from blockchain import Blockchain
import sys

blockchain = Blockchain()

app = Flask(__name__)
PORT = int(sys.argv[1])


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_nonce = previous_block['nonce']
    nonce = blockchain.proof_of_work(previous_nonce)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(nonce, previous_hash)
    response = {
        'message': "Congratulations! New bock have been mined",
        'index': block['index'],
        'timestamp': block['timestamp'],
        'nonce': block['nonce'],
        'transactions': block['transactions'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    transaction = request.json
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in transaction for key in transaction_keys):
        response = {
            'message': "Transaction error",
            'transaction': transaction
        }
        return jsonify(response), 400
    blockchain.add_transaction(transaction)
    response = {
        'message': "Transaction registered",
        'transaction': transaction
    }
    return jsonify(response), 201


@app.route('/add_nodes', methods=['POST'])
def add_nodes():
    data = request.json
    nodes = data['nodes']
    if not nodes:
        response = {
            'message': "Not nodes to add",
        }
        return jsonify(response), 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': "All nodes added to blockchain",
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    chain_replaced = blockchain.replace_chain()
    if chain_replaced:
        response = {
            'message': "Nodes have different chains , current chain updated to longest chain",
            'current_blockchain': blockchain.chain
        }
    else:
        response = {
            'message': "All seems OK, this chain is currently the longest chain",
            'current_blockchain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/is_valid',  methods=['GET'])
def is_valid():
    valid_chain = blockchain.valid_chain(blockchain.chain)
    if valid_chain:
        response = {'message': "Blockchain is valid"}
    else:
        response = {'message': "Blockchain is not valid"}
    return jsonify(response), 200


app.run(host='127.0.0.1', port=PORT, debug=True)
