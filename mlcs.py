import collections
import heapq
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
    keyPaths = {initialKey: [()]}
    fringe = [initialKey]
    maxDAGLength = 1
    keysConsidered = 0
    result = []
    while fringe:
        maxDAGLength = max(maxDAGLength, len(fringe))
        key = heapq.heappop(fringe)
        paths = keyPaths.pop(key)
        nodeHasChildren = False
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

            keysConsidered += 1

            if len(childKey) < minCycleCount:
                continue

            nodeHasChildren = True

            try:
                childPaths = keyPaths[childKey]
            except KeyError:
                childPaths = []
                heapq.heappush(fringe, childKey)

            keyPaths[childKey] = keepLongest(
                childPaths,
                [path + (childToken,) for path in paths]
            )

        if not nodeHasChildren:
            result = keepLongest(result, paths)

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

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

if __name__ == '__main__':
    print(*mlcs('actagcta'), sep='\n')
    # time complexity: 15
    # space complexity: 3
    # acta
