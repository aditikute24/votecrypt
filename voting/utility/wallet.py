from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
import Crypto.Random
import binascii
from django.conf import settings
import os

# Wallet class that handles key generation,
# saving, loading, signing, and verifying transactions in a blockchain context. 

class Wallet:

    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (
            binascii.hexlify(private_key.exportKey(format = 'DER')).decode('ascii'),
            binascii.hexlify(public_key.exportKey(format = 'DER')).decode('ascii')
        )

    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()
        print (self.private_key, self.public_key)

    def save_keys(self):
        if self.private_key is not None and self.public_key is not None:
            #print (self.node_id[:6])
            #location = os.path.join(settings.BASE_DIR, 'utility/wallet-{}.txt'.format(str(self.node_id)))
            try:
                location = os.path.join(settings.BASE_DIR, 'utility/wallet-{}.txt'.format(str(self.node_id)))
                #print ("Location", location)
                with open(location, mode = 'w') as f:
                    #print ("Opened")
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except(IOError, IndexError):
                print ("Saving wallet failed!")
                return False

    def load_keys(self):
        try:
            location = os.path.join(settings.BASE_DIR, 'utility/wallet-{}.txt'.format(str(self.node_id)))
            with open(location, mode = 'r') as f:
            #with open('wallet-{}.txt'.format(self.node_id), mode = 'r') as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
                return True
        except(IOError, IndexError):
            print ("Loading wallet failed!")
            return False

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))


