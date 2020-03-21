import bisect
import collections
import heapq
import itertools
from referenceCounter import ReferenceCounter
from successorTable import SuccessorTable

def mlcs(sequence, minCycleCount=2):
    alphabet = {
        token for token, count in collections.Counter(sequence).items() \
            if count >= minCycleCount
    }
    table = SuccessorTable(sequence, alphabet)
    # Invariants:
    # -key.cycleCount <= -key.child.cycleCount
    # key.firstCycleStop < key.child.firstCycleStop
    # Consequently, key < key.child
    # Therefore by the time a key is popped from the heap,
    # all its parents have already been expanded.
    keyPaths = {
        (
            -len(positions), # cycleCount (negative)
            positions[0] + 1, # firstCycleStop
            tuple((p, p + 1) for p in positions[1:]), # cycleRanges
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
        cycleCount, firstCycleStop, cycleRanges = key
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
            lastTokenPosition = table.tokenPositions[childToken][-1]
            if firstCycleStop > lastTokenPosition:
                continue

            firstChildCycleStop = 1 + table.index(
                childToken,
                start=firstCycleStop
            )

            tempCycleRanges = [
                (
                    start,
                    1 + table.index(childToken, start=stop)
                ) \
                    for start, stop in cycleRanges \
                        if stop <= lastTokenPosition
            ]
            childCycleRanges = tuple(getNonDominatedRanges(
                tempCycleRanges,
                minStart=firstChildCycleStop
            ))

            childCycleCount = 1 + sum(
                1 for _ in getNonOverlapping(childCycleRanges)
            )
            if childCycleCount < minCycleCount:
                continue

            childKey = (
                -childCycleCount,
                firstChildCycleStop,
                childCycleRanges
            )
            try:
                existingChildPaths = keyPaths[childKey]
            except KeyError:
                existingChildPaths = []
                heapq.heappush(fringe, childKey)

            newChildPaths = [
                path + (childToken,) for path in paths
            ]

            keyPaths[childKey] = keepLongest(
                existingChildPaths,
                newChildPaths
            )

    yield prevCycleCount, result

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

def getNonDominatedRanges(ranges, minStart = float('-inf')):
    """Preconditions:
    ranges[i].start <= ranges[i + 1].start
    ranges[i].stop <= ranges[i + 1].stop
    """
    return (
        lastRange \
            for _, (*_, lastRange) in itertools.groupby(
                ranges,
                lambda range: range[1]
            ) \
                if lastRange[0] >= minStart
    )

def getNonOverlapping(ranges):
    """Precondition: ranges are sorted by (start, stop)
    """
    lastStop = float('-inf') # pylint: disable=unused-variable
    return (
        (start, lastStop := stop)
            for start, stop in ranges \
                if start >= lastStop
    )

assert list(getNonOverlapping(
    [(1, 4), (2, 5), (3, 6), (6, 8), (7, 9), (8, 10), (10, 12)]
)) == [(1, 4), (6, 8), (8, 10), (10, 12)]

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
    results = mlcs('abacbadcbdcd')
    for cycleCount, result in results:
        print(cycleCount)
        print(*result, sep='\n')
    # time complexity: 72
    # space complexity: 8
    # ab
    # bc
    # cd
    # bac
    # abc
    # acb
    # cbd
    # bcd
    # bdc
