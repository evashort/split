import bisect
import collections

class PatternFinder:
    def __init__(self, tokens, minTokenCount=2):
        self.minTokenCount = minTokenCount

        tokenCounts = collections.Counter(tokens)
        self.tokenIndices = multidict(
            (token, i) \
                for i, token in enumerate(tokens) \
                    if tokenCounts[token] >= self.minTokenCount
        )

    def getRepeatedTokens(self):
        return self.tokenIndices.keys()

    def getTotalLength(self, pattern):
        start = 0
        totalLength = 0
        try:
            while True:
                for token in pattern:
                    start = self.index(token, start) + 1
                    totalLength += 1
        except ValueError:
            return totalLength

    def getCycleCount(self, pattern):
        totalLength = self.getTotalLength(pattern)
        return divmod(totalLength, len(pattern))

    def enoughCycles(self, cycleCount):
        return cycleCount >= (self.minTokenCount, 0)

    def index(self, token, start=0, stop=float('inf')):
        try:
            indices = self.tokenIndices[token]
        except KeyError:
            raise ValueError(f'token not found: {token}')

        iIndex = bisect.bisect_left(indices, start)
        try:
            i = indices[iIndex]
        except IndexError:
            raise ValueError(
                f'token not found in range [{start}, inf): {token}'
            )

        if i >= stop:
            raise ValueError(
                f'token not found in range [{start}, {stop}): {token}'
            )

        return i

def multidict(items):
    result = {}
    for k, v in items:
        result.setdefault(k, []).append(v)

    return result
