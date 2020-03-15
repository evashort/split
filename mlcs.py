import bisect
import collections
import heapq
from referenceCounter import ReferenceCounter
from successorTable import SuccessorTable

def mlcs(sequence, minCycleCount=2):
    alphabet = {
        token for token, count in collections.Counter(sequence).items() \
            if count >= minCycleCount
    }
    table = SuccessorTable(sequence, alphabet)
    keyPaths = {
        (
            -len(positions),
            tuple(positions),
            tuple(positions)
        ): [
            (token,)
        ] \
            for token, positions in table.tokenPositions.items()
    }
    fringe = list(keyPaths)
    heapq.heapify(fringe)
    maxDAGLength = 1
    keysConsidered = 0
    prevCycleCount = float('inf')
    result = []
    while fringe:
        maxDAGLength = max(maxDAGLength, len(fringe))
        key = heapq.heappop(fringe)
        cycleCount, startPoint, matchPoint = key
        cycleCount = -cycleCount
        paths = keyPaths.pop(key)
        if cycleCount < prevCycleCount:
            if prevCycleCount < float('inf'):
                yield prevCycleCount, result
            result = []
            prevCycleCount = cycleCount

        result = keepLongest(
            result,
            paths
        )
        for childToken in alphabet:
            keysConsidered += 1
            lastPosition = table.tokenPositions[childToken][-1]
            childMatchPoint = tuple(sorted({
                table.index(childToken, start=position+1) \
                    for position in matchPoint \
                        if position < lastPosition
            }))
            indexMap = [
                bisect.bisect_left(matchPoint, position) - 1 \
                    for position in childMatchPoint
            ]
            childStartPoint = tuple(
                startPoint[i] for i in indexMap
            )

            childCycleCountPaths = {}
            for path in paths:
                childPath = path + (childToken,)
                childCycleCount \
                    = len(table.indexCycle(childPath)) // len(childPath)
                if childCycleCount < minCycleCount:
                    continue

                childPaths = childCycleCountPaths.setdefault(childCycleCount, [])
                childPaths.append(childPath)

            for childCycleCount, childPaths in childCycleCountPaths.items():
                childKey = (
                    -childCycleCount,
                    childStartPoint,
                    childMatchPoint
                )

                try:
                    oldChildPaths = keyPaths[childKey]
                except KeyError:
                    oldChildPaths = []
                    heapq.heappush(fringe, childKey)

                keyPaths[childKey] = keepLongest(
                    oldChildPaths,
                    childPaths
                )

    yield prevCycleCount, result

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

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
    results = mlcs('actagcta')
    for cycleCount, result in results:
        print(cycleCount)
        print(*result, sep='\n')
    # time complexity: 24
    # space complexity: 4
    # a
    # act
    # cta
