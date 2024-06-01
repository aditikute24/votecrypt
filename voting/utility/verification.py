from .wallet import Wallet
from .hash_util import hash_string_256, hash_block

class Verification:

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds = True):
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return (sender_balance >= transaction.amount and Wallet.verify_transaction(transaction))
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        h = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        #print (h)
        guess = hash_string_256(h)
        #print (guess)
        return guess[0:2] == '00'