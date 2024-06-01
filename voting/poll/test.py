from collections import OrderedDict
import pickle

with open('poll.ovs', mode = 'rb') as f:
    print ("opened")
    y = (pickle.loads(f.read()))
    print (y)
