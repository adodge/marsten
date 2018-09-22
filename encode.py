#!/usr/bin/env python
import sys
import pickle
with open(sys.argv[1], 'rb') as fd:
    C = pickle.load(fd)

sys.stdout.write(C.encode(sys.stdin.buffer.read(), verbose=True))
