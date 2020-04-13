import sortedcontainers # pip install sortedcontainers

class NDS2D:
    def __init__(self):
        self.members = sortedcontainers.SortedList()

    def add(self, item):
        i = self.members.bisect_left(item)
        if i > 0:
            lowerItem = self.members[i - 1]
            if lowerItem[1] <= item[1]:
                return False

        if i < len(self.members):
            oldItem = self.members[i]
            if oldItem == item:
                return False

            while oldItem[1] >= item[1]:
                del self.members[i]
                if i >= len(self.members):
                    break

                oldItem = self.members[i]

        self.members.add(item)
        return True

    def __len__(self):
        return len(self.members)

    def __iter__(self):
        return iter(self.members)

    def clear(self):
        self.members.clear()

if __name__ == '__main__':
    import collections
    import random

    def dominates(a, b):
        return a < b and a[1] <= b[1]

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

        nds2D = NDS2D()
        for vector in testData:
            nds2D.add(vector)

        assert set(nds2D) == naiveNDS
        assert len(nds2D) == len(naiveNDS)
