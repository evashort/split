import heapq

class PriorityDict(dict):
    def __init__(
        self,
        getPriority,
        iterableOrMapping=(),
        /,
        **kwargs
    ):
        '''getPriority(key, value) => priority
        '''
        super().__init__(iterableOrMapping, **kwargs)
        self.getPriority = getPriority
        self._fix()

    def popitem(self):
        _, key = self.heap[0]
        return key, self.pop(key)

    def peekitem(self):
        _, key = self.heap[0]
        return key, self[key]

    def setdefault(self, key, default=None):
        value = super().setdefault(key, default)
        if key not in self.keyIndices:
            priority = self.getPriority(key, value)
            self.heap.append((priority, key))
            self.bubbleUp(len(self.heap) - 1)

        return value

    def pop(self, key, *args):
        value = super().pop(key, *args)
        try:
            i = self.keyIndices.pop(key)
        except KeyError:
            return value

        if i == len(self.heap) - 1:
            self.heap.pop()
        else:
            self.heap[i] = self.heap.pop()
            self.bubbleDown(i)

        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        priority = self.getPriority(key, value)
        try:
            i = self.keyIndices[key]
        except KeyError:
            self.heap.append((priority, key))
            self.bubbleUp(len(self.heap) - 1)
            return

        oldPriority, _ = self.heap[i]
        self.heap[i] = (priority, key)
        if priority < oldPriority:
            self.bubbleUp(i)
        elif priority > oldPriority:
            self.bubbleDown(i)

    def __delitem__(self, key):
        super().__delitem__(key)
        i = self.keyIndices.pop(key)
        if i == len(self.heap) - 1:
            self.heap.pop()
        else:
            self.heap[i] = self.heap.pop()
            self.bubbleDown(i)

    def update(self, iterableOrMapping, **kwargs):
        super().update(iterableOrMapping, **kwargs)
        self._fix()

    def clear(self):
        super().clear()
        self.heap.clear()
        self.keyIndices.clear()

    def copy(self):
        result = super().copy()
        result.getPriority = self.getPriority
        result.heap = self.heap.copy()
        result.keyIndices = self.keyIndices.copy()
        result.__class__ = self.__class__
        return result

    @classmethod
    def fromkeys(cls, getPriority, keys, value=None):
        return cls(
            getPriority,
            ((key, value) for key in keys)
        )

    def bubbleUp(self, i):
        tmp = self.heap[i]
        while self.heap[i] < self.heap[
            (parent := self.parent(i))
        ]:
            self._set(i, self.heap[parent])
            i = parent

        self._set(i, tmp)

    def bubbleDown(self, i):
        tmp = self.heap[i]
        while self.heap[i] > self.heap[
            (child := self.minChild(i))
        ]:
            self._set(i, self.heap[child])
            i = child

        self._set(i, tmp)

    def parent(self, i):
        return max(0, (i - 1) // 2)

    def minChild(self, i):
        firstChild = i * 2 + 1
        if firstChild >= len(self.heap):
            return i
        elif firstChild == len(self.heap) - 1:
            return firstChild
        elif self.heap[firstChild] <= self.heap[firstChild + 1]:
            return firstChild
        else:
            return firstChild + 1

    def _set(self, i, pair):
        self.heap[i] = pair
        _, key = pair
        self.keyIndices[key] = i

    def _fix(self):
        self.heap = [
            (self.getPriority(key, value), key) \
                for key, value in self.items()
        ]
        heapq.heapify(self.heap)
        self.keyIndices = {
            key: i for i, (_, key) in enumerate(self.heap)
        }

    def getPriority(self, key, value):
        raise NotImplementedError(
            'this is just to make pylint stop complaining'
        )

if __name__ == '__main__':
    import random
    random.seed(0)
    getPriority = lambda k, v: k + v
    control = {}
    subject = PriorityDict(getPriority)
    for i in range(1000):
        k = random.randrange(10)
        v = random.randrange(10)
        operation = random.choice(
            ['setdefault', 'pop', 'set', 'del']
        )
        if operation == 'setdefault':
            control.setdefault(k, v)
            subject.setdefault(k, v)
        elif operation == 'pop':
            control.pop(k, v)
            subject.pop(k, v)
        elif operation == 'set':
            control[k] = v
            subject[k] = v
        elif operation == 'del':
            try:
                del control[k]
            except KeyError:
                pass
            try:
                del subject[k]
            except KeyError:
                pass

        assert subject == control

    controlItems = sorted(
        control.items(),
        key=lambda item: getPriority(item[0], item[1])
    )
    subjectItems = []
    while subject:
        subjectItems.append(subject.popitem())

    assert subjectItems == controlItems
