import sortedcontainers # pip install sortedcontainers

class NDS2D:
    def __init__(self, key=None, duplicates='keep'):
        '''
        duplicates: keep, skip, or replace
        '''
        self.members = sortedcontainers.SortedList(key=key)
        if key is not None:
            self.key = key

        self.duplicates = duplicates

    def key(self, value): # pylint: disable=method-hidden
        return value

    def add(self, value):
        newKey = self.key(value)

        i = self.members.bisect_left(value)
        if i > 0:
            lowerKey = self.key(self.members[i - 1])
            if lowerKey[1] <= newKey[1]:
                return False

        if self.duplicates == 'keep':
            i = self.members.bisect_right(value)

        if i < len(self.members):
            oldKey = self.key(self.members[i])
            if self.duplicates == 'skip' and oldKey == newKey:
                return False

            while oldKey[1] >= newKey[1]:
                del self.members[i]
                if i >= len(self.members):
                    break

                oldKey = self.key(self.members[i])

        self.members.add(value)
        return True

    def __len__(self):
        return len(self.members)

    def __iter__(self):
        return iter(self.members)

    def __reversed__(self):
        return reversed(self.members)

    def __getitem__(self, index):
        return self.members[index]

    def clear(self):
        self.members.clear()

if __name__ == '__main__':
    import collections
    import random

    def dominates(a, b):
        return a < b and a[1] <= b[1]

    for duplicates in ['keep', 'skip', 'replace']:
        random.seed('reproducible test data 1')
        for i in range(1000):
            testData = [
                tuple(random.randrange(10) for i in range(2)) \
                    for i in range(30)
            ]
            naiveNDS = {
                vector for vector in testData if not any(
                    dominates(other, vector) \
                        for other in testData \
                            if other != vector
                )
            }
            if duplicates == 'keep':
                vectorCounts = collections.Counter(testData)
                expectedLength = sum(
                    vectorCounts[vector] for vector in naiveNDS
                )
            else:
                expectedLength = len(naiveNDS)

            nds2D = NDS2D(duplicates=duplicates)
            for vector in testData:
                nds2D.add(vector)

            assert set(nds2D) == naiveNDS
            assert len(nds2D) == expectedLength
