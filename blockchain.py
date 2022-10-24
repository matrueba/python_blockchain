import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse


class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(nonce=1, previous_hash='0')
        self.nodes = set()
        #self.get_connected_nodes

    def get_connected_nodes(self):
        response = requests.get('http://127.0.0.1/get_nodes')
        connected_nodes = response.json()
        for node in connected_nodes:
            self.add_node(node)

    def create_block(self, nonce, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    @ staticmethod
    def proof_of_work(previous_nonce):
        new_nonce = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_nonce += 1
        return new_nonce

    @staticmethod
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        hash_block = hashlib.sha256(encoded_block).hexdigest()
        return hash_block

    def valid_chain(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce ** 2 - previous_nonce ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get("http://{}/get_chain".format(node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
