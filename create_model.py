#!/usr/bin/env python
import sys
from marsten.markov import Markov
from marsten.codec import MarstenCodec

G = "\n".join( open(x).read() for x in sys.argv[2:] )
M = Markov(history=6).fit(G)
C = MarstenCodec(M)

import pickle
with open(sys.argv[1], 'wb') as fd:
    pickle.dump(C, fd, protocol=4)
