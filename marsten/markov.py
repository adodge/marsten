import numpy as np
from collections import defaultdict,Counter
import itertools


class Markov(object):
    def __init__(self, history=1):
        self.history = history
        self._fitted = False

    def fit(self, X):
        """
        Can be called multiple times, which will continue to update the same model.
        """
        if not self._fitted:
            self._fitted = True
            self.model_ = defaultdict(Counter)
            self.types_ = set()

        documents = self.tokenize(X)

        for DOC in documents:
            history = [None]*self.history
            for tok in itertools.chain(DOC, [None]):
                self.types_.add(tok)
                self.model_[tuple(history)][tok] += 1
                history = history[1:]+[tok]

        return self

    def _key(self, x):
        if x[0] is None:
            return (0,)
        else:
            return (1, x[0])

    def transitions(self, history=None):
        if history is None:
            history = [None]*self.history

        steps = self.model_[tuple(history)]

        S = sorted(steps.items(), key=self._key)
        probs = np.array( [v for s,v in S] )
        probs = probs / probs.sum()

        return [ (p, tok, tuple(list(history[1:])+[tok])) for p,tok in zip(probs, [s for s,v in S]) ]

    def serialize(self, X):
        """
        Take a list of lists of tokens and produce a cyphertext.
        """
        return "\n".join("".join(x) for x in X)

    def tokenize(self, X):
        """
        Take a cyphertext and produce a list of lists of tokens.
        """
        return [list(x) for x in X.split("\n")]
