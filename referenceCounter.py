import collections

class ReferenceCounter:
    def __init__(self, references=None):
        self.counter = collections.Counter(references)
        self.garbage = {
            key for key, count in self.counter.items() \
                if not count
        }
        for key in self.garbage:
            del self.counter[key]

    def add(self, key):
        self.garbage.discard(key)
        self.counter[key] += 1

    def remove(self, key):
        if self.counter[key] == 1:
            del self.counter[key]
            self.garbage.add(key)
        elif self.counter[key]:
            self.counter[key] -= 1
        else:
            raise ValueError(
                f'removal of non-existant key {key}'
            )

    def getGarbage(self):
        oldGarbage = self.garbage
        self.garbage = set()
        return oldGarbage
