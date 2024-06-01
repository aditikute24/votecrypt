from collections import OrderedDict
import pickle

with open('poll.ovs', mode = 'wb') as f:
    print ("opened")
    y = OrderedDict([('polls', []), ('length', 0)])
    f.write(pickle.dumps(y))

    
