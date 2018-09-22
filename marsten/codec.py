import sys
import numpy as np

class MarstenCodec(object):
    def __init__(self, model, margin=0.1):
        """
        Only use nodes that have a partition that splits the decision space in
        half with less than `margin` error.  For example, 10% margin means only
        nodes with a partition consisting of between 45% and 55% of the
        probability density will be used to encode a message.  Lower values
        mean less detectible encoding, but also longer messages.
        """
        self.model = model
        self.margin = margin

    def _partition(self, X):
        """
        Use a greedy heuristic to find a near-half partition. `X` are tuples
        where the first element is the score.  Returns a tuple:
            * Boolean that's true if the partition quality is within the margin
            * Partition 0
            * Partition 1
        """
        X.sort(key=lambda x:x[0])
        P0,P1 = [],[]
        for i,x in enumerate(X):
            if i%2 == 0:
                P0.append(x)
            else:
                P1.append(x)

        Z0 = sum(x[0] for x in P0)
        ok = .5 - self.margin/2 < Z0 < .5 + self.margin/2
        return ok,P0,P1


    def _encode(self, data):
        """
        Given a data block (as a bytes object), encode as much as possible using the given model.
        Returns the encoded representation and the remaining data.  If a whole
        byte is not encoded, it is returned unchanged as part of the remaining
        data.  It's up to the decoder to discard incomplete bytes at the end of messages.
        """

        byteidx = 0
        bitidx = 0
        finished = False

        message = []

        s0 = None
        while True:
            T = self.model.transitions(s0)
            if not finished:
                ok,P0,P1 = self._partition(T)
                if ok:
                    bitval = data[byteidx]&(0x1 << bitidx) == 0
                    T = P1 if bitval else P0

                    bitidx += 1
                    if bitidx == 8:
                        byteidx += 1
                        bitidx = 0
                        if byteidx >= len(data):
                            finished = True
                
            Z = sum(a for a,b,c in T)
            i = np.random.choice(range(len(T)), size=2, p=[a/Z for a,b,c in T])[0]
            _,tok,s0 = T[i]
            if tok is None or finished:
                break
            message.append(tok)
        return message, data[byteidx:]

    def _decode(self, message):

        data = []
        byte = []
        bitidx = 0

        s0 = None
        for tok in message:
            T = self.model.transitions(s0)
            ok,P0,P1 = self._partition(T)
            if not ok:
                s0 = {b:c for a,b,c in T}[tok]
                continue
            
            T0 = {b:c for a,b,c in P0}
            T1 = {b:c for a,b,c in P1}

            if tok not in T0 and tok not in T1:
                raise Exception("Unknown transition.")

            if tok in T0:
                byte.append(1)
                s0 = T0[tok]
            elif tok in T1:
                byte.append(0)
                s0 = T1[tok]

            bitidx += 1
            if bitidx == 8:
                bitidx = 0
                b = 0
                for i,v in enumerate(byte):
                    b += v << i
                data.append(b)
                byte = []

        return bytes(data)

    def encode(self, plaintext):
        code = []
        while plaintext:
            code0,plaintext = self._encode(plaintext)
            code.append(code0)
        return self.model.serialize(code)

    def decode(self, code):
        message = b''
        for c in self.model.tokenize(code):
            b = self._decode(c)
            message += b
        return message
