from utility.block import Block
from utility.wallet import Wallet
from utility.transaction import Transaction
from utility.verification import Verification
import pickle
from functools import reduce
from .hash_util import hash_block
from django.conf import settings
import os

class Blockchain:

    def __init__(self, public_key, node_id = 600):
        genesis_block = Block(0, '', [], 100, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    '''@property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]'''

    def save_data(self):
        try:
            location = os.path.join(settings.BASE_DIR, 'utility/blockchain-{}.ovs'.format(self.node_id))
            with open(location, mode = 'wb') as f:
                save_data_obj = {
                    'chain':self.__chain,
                    'open_tx':self.__open_transactions,
                    'peer_nodes':self.__peer_nodes
                }
                print(save_data_obj)
                f.write(pickle.dumps(save_data_obj))
        except IOError:
            print ("Saving failed!")

    def load_data(self):
        try:
            location = os.path.join(settings.BASE_DIR, 'utility/blockchain-{}.ovs'.format(self.node_id))
            with open(location, mode = 'rb') as f:
                file_content = pickle.loads(f.read())
                self.__chain = file_content['chain']
                self.__open_transactions = file_content['open_tx']
                self.__peer_nodes = file_content['peer_nodes']
                #print (self.__chain)
                #print (self.__open_transactions)
        except (IOError, IndexError):
            print ("Loading failed!")

    def create_dummy(self):
        tobj = [
            Transaction(
                '30819f300d06092a864886f70d010101050003818d0030818902818100f1ec17621e9bab4a28ecb09b6216d4b2d8c6151bad1c6af8db74da457c59ee446a5e1dd6757d15e0e45b9eb71661c1d9ab345918f91478945b479d4c7343ae179a1ba1734783ea3d79eba71ac76b5f365eab39ff0b4d1b5a2cbe5f0e5a49f72a604f4720514795a6b62bed63f3aafff4f2f50ade6175aa2e35cd350df35182090203010001', 'b', 'asdasdasd', e
            ) for e in range(0, 5)
        ]

        tobj.append(Transaction(
                '542656230819f300d06092a864886f70d010101050003818d0030818902818100f1ec17621e9bab4a28ecb09b6216d4b2d8c6151bad1c6af8db74da457c59ee446a5e1dd6757d15e0e45b9eb71661c1d9ab345918f91478945b479d4c7343ae179a1ba1734783ea3d79eba71ac76b5f365eab39ff0b4d1b5a2cbe5f0e5a49f72a604f4720514795a6b62bed63f3aafff4f2f50ade6175aa2e35cd350df35182090203010001', '30819f300d06092a864886f70d010101050003818d0030818902818100f1ec17621e9bab4a28ecb09b6216d4b2d8c6151bad1c6af8db74da457c59ee446a5e1dd6757d15e0e45b9eb71661c1d9ab345918f91478945b479d4c7343ae179a1ba1734783ea3d79eba71ac76b5f365eab39ff0b4d1b5a2cbe5f0e5a49f72a604f4720514795a6b62bed63f3aafff4f2f50ade6175aa2e35cd350df35182090203010001', 'asdasdasd', 6
            ))

        blockobj = Block(
            1, 'asdasd', tobj, 100, 0
        )

        print (tobj)
        print (blockobj)

        print (self.__chain.append(blockobj))
        print (self.__chain)
        
        
    def get_balance(self, sender = None):
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender
        tx_sender = [
            [
                tx.amount for tx in block.transactions if tx.sender == participant
            ] for block in self.__chain
        ]
        open_tx_sender = [
            tx.amount for tx in self.__open_transactions if tx.sender == participant
        ]
        tx_sender.append(open_tx_sender)
        #print (tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        #print (amount_sent)
        tx_recipient = [
            [
                tx.amount for tx in block.transactions if tx.recipient == participant
            ] for block in self.__chain
        ]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        return amount_received - amount_sent


    def add_transaction(self, sender, recipient, signature, amount = 1.0):
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance, False):
            self.__open_transactions.append(transaction)
            self.save_data()
            print (self.__open_transactions)
            return True
        return False

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1

        return proof

    def mine_block(self):
        if self.public_key is None:
            return None
        previous_block_hash = hash_block(self.__chain[-1])
        proof = self.proof_of_work()

        for tx in self.__open_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        
        block = Block(len(self.__chain), previous_block_hash, self.__open_transactions[:], proof)

        self.__chain.append(block)
        self.__open_transactions = []

        self.save_data()

        return block

    def check_user_poll(self, sender, recipient):
        for block in self.__chain:
            for tx in block.transactions:
                if tx.sender == sender:
                    if tx.recipient == recipient:
                        return True

        for tx in self.__open_transactions:
            if tx.sender == sender:
                if tx.recipient == recipient:
                    return True
        return False


    def check_vote_count(self, recipient, amount):
        #print ("in function")
        count = 0
        for block in self.__chain:
            #print ("block", block)
            for tx in block.transactions:
                #print ("tx is ", tx)
                if tx.recipient == recipient:
                    #print ("poll is ", tx.recipient)
                    if tx.amount == amount:
                        #print ("amount is ", tx.amount)
                        count += 1

        for tx in self.__open_transactions:
            if tx.recipient == recipient:
                if tx.amount == amount:
                    #print ("amount is ", tx.amount)
                    count += 1
        return count










    
