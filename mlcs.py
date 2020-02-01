import collections
from referenceCounter import ReferenceCounter
from successorTable import SuccessorTable

def mlcs(sequence, minCycleCount=2):
    # https://www.frontiersin.org/articles/10.3389/fgene.2017.00104/full
    alphabet = {
        token for token, count in collections.Counter(sequence).items() \
            if count >= minCycleCount
    }
    table = SuccessorTable(sequence, alphabet)
    initialKey = None
    leveledDAG = {initialKey: Node()}
    parentCounts = ReferenceCounter({initialKey: 0})
    fringe = [initialKey]
    result = []
    while leveledDAG:
        newFringe = []
        for key in fringe:
            node = leveledDAG[key]
            for childToken in alphabet:
                if key is None:
                    childKey = tuple(table.tokenPositions[childToken])
                else:
                    childKey = tuple(
                        uniq(
                            takeUntilError(
                                ValueError,
                                (
                                    table.index(childToken, position + 1) \
                                        # pylint: disable=not-an-iterable
                                        for position in key
                                )
                            )
                        )
                    )

                if len(childKey) < minCycleCount:
                    continue

                node.children.append(childKey)
                parentCounts.add(childKey)
                if childKey not in leveledDAG:
                    leveledDAG[childKey] = Node()
                    newFringe.append(childKey)

        fringe = newFringe

        for key in parentCounts.getGarbage():
            node = leveledDAG.pop(key)
            if key is None:
                childPaths = [[]]
            else:
                token = sequence[key[0]]
                childPaths = [path + [token] for path in node.paths]

            for childKey in node.children:
                parentCounts.remove(childKey)
                childNode = leveledDAG[childKey]
                childNode.paths = keepLongest(childNode.paths, childPaths)

            if not node.children:
                result = keepLongest(result, childPaths)

    return result

def takeUntilError(exception, iterable):
    try:
        yield from iterable
    except exception:
        pass

def uniq(iterable):
    iterator = iter(iterable)
    try:
        prevItem = next(iterator)
    except StopIteration:
        return

    yield prevItem
    yield from (
        (prevItem := item) for item in iterator \
            if item != prevItem
    )

def keepLongest(*pathLists):
    maxLength = max(
        len(paths[0]) for paths in filter(None, pathLists)
    )
    result = []
    for paths in filter(None, pathLists):
        if len(paths[0]) == maxLength:
            result += paths

    return result

class Node:
    def __init__(self):
        self.children = []
        self.paths = []

if __name__ == '__main__':
    print(*mlcs('actagcta'), sep='\n')
    # acta
