import collections
import heapq
import itertools
import nonDominated
from successorTable import SuccessorTable, multidict

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
            -len(table.tokenPositions[token]), # cycleCount (negative)
            table.index(token) + 1, # firstCycleStop
            tuple(
                (p, p + 1) for p in table.tokenPositions[token][1:]
            ), # cycleRanges
        ): {
            # path
            (token,): [
                (
                    float('inf'), # partialStart
                    0 # partialLength
                )
            ] # partials
        } \
            for token in alphabet
    }
    fringe = list(keyPaths)
    heapq.heapify(fringe)
    maxDAGLength = 1
    keysConsidered = 0
    prevCycleCount = float('inf')
    minPathLength = 1
    result = []
    while fringe:
        maxDAGLength = max(maxDAGLength, len(fringe))
        key = heapq.heappop(fringe)
        cycleCount, firstStop, cycleRanges = key
        cycleCount = -cycleCount
        *_, (_, lastStop) = nonOverlapping(cycleRanges)
        pathPartials = keyPaths.pop(key)
        if cycleCount < prevCycleCount:
            if prevCycleCount < float('inf'):
                result.sort(
                    key=lambda item: item[4], # partialLength
                    reverse=True
                )
                for item in result:
                    if not hasSubcycle(item[0]):
                        yield getPathPositions(*item, table)

            minPathLength = 1 + max(
                len(path) for path, *_ in result
            ) \
                if result else minPathLength
            result = []
            prevCycleCount = cycleCount

        pathItems = (
            (
                path,
                firstStop,
                tuple(nonOverlapping(cycleRanges)),
                partialStart,
                partialLength
            ) \
                for path, partials in pathPartials.items() \
                    for partialStart, partialLength in partials \
                        if partialStart >= lastStop \
                            and len(path) >= minPathLength
        )
        result = nonDominated.nonDominated(
            [*result, *pathItems],
            key=lambda item: (
                len(item[0]), # cycleLength
                item[4] # partialLength
            )
        )

        for childToken in alphabet:
            keysConsidered += 1

            # extend each range by including the next occurrence of
            # childToken, removing any ranges that overlap the first range
            # note: partial ranges that overlap the first range don't need to
            # be removed because at that point there is only one cycle anyway
            childFirstStop = 1 + table.index(childToken, start=firstStop)
            extendedRanges = [
                (
                    start,
                    1 + table.index(childToken, start=stop)
                ) \
                    for start, stop in cycleRanges \
                        if start >= childFirstStop
            ]

            # remove dominated ranges by picking the latest start for each
            # distinct value of stop
            nonDominatedRanges = [
                lastRange \
                    for _, (*_, lastRange) in itertools.groupby(
                        extendedRanges,
                        lambda range: range[1]
                    )
            ]

            # check if final range is now partial
            if nonDominatedRanges \
                and nonDominatedRanges[-1][1] == float('inf'):
                newPartialStart, _ = nonDominatedRanges.pop()
                newPartialLength = max(map(len, pathPartials))
            else:
                newPartialLength = float('inf')

            childCycleCount = 1 + sum(
                1 for i in nonOverlapping(nonDominatedRanges)
            )
            if childCycleCount < minCycleCount:
                continue

            newPathPartials = {
                path + (childToken,): (
                    partials + [
                        (newPartialStart, newPartialLength)
                    ] \
                        if len(path) == newPartialLength \
                            else partials
                ) \
                    for path, partials in pathPartials.items()
            }

            childKey = (
                -childCycleCount,
                childFirstStop,
                tuple(nonDominatedRanges)
            )
            try:
                existingPathPartials = keyPaths[childKey]
            except KeyError:
                childPathPartials = newPathPartials
                heapq.heappush(fringe, childKey)
            else:
                childItems = nonDominated.nonDominated(
                    [
                        *flatItems(existingPathPartials),
                        *flatItems(newPathPartials)
                    ],
                    key=lambda item: (
                        len(item[0]), # cycleLength
                        item[1][0], # partialStart
                        item[1][1], # partialLength
                    )
                )
                childPathPartials = multidict(childItems)

            keyPaths[childKey] = childPathPartials

    result.sort(
        key=lambda item: item[4], # partialLength
        reverse=True
    )
    for item in result:
        if not hasSubcycle(item[0]):
            yield getPathPositions(*item, table)

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

def flatItems(multiDict):
    return (
        (key, value) \
            for key, values in multiDict.items() \
                for value in values
    )

def nonOverlapping(ranges):
    """Precondition: ranges are sorted by (start, stop)
    """
    lastStop = float('-inf') # pylint: disable=unused-variable
    return (
        (start, lastStop := stop)
            for start, stop in ranges \
                if start >= lastStop
    )

assert list(nonOverlapping(
    [(1, 4), (2, 5), (3, 6), (6, 8), (7, 9), (8, 10), (10, 12)]
)) == [(1, 4), (6, 8), (8, 10), (10, 12)]

def getPathPositions(
    path,
    firstStop,
    cycleRanges,
    partialStart,
    partialLength,
    table
):
    result = [firstStop - 1]
    for token in path[-2::-1]:
        result.append(
            table.rindex(token, end=result[-1] - 1)
        )

    result.reverse()

    for cycleStart, _ in cycleRanges:
        result.append(cycleStart)
        for token in path[1:]:
            result.append(
                table.index(token, start=result[-1] + 1)
            )

    if partialLength:
        result.append(partialStart)
        for token in path[1:partialLength]:
            result.append(
                table.index(token, start=result[-1] + 1)
            )

    return len(path), result

def hasSubcycle(sequence):
    for cycleLength in range(1, len(sequence) // 2 + 1):
        cycleCount, remainder = divmod(len(sequence), cycleLength)
        if remainder:
            continue

        if sequence == sequence[:cycleLength] * cycleCount:
            return True

    return False

def printResults(input, sep='', indent='    '):
    if len(input) < 80:
        print()
        print(input)

    results = mlcs(input)
    oldCycleCount = (0, 0)
    for cycleLength, positions in results:
        cycleCount = divmod(len(positions), cycleLength)
        if cycleCount != oldCycleCount:
            print(f'*{cycleCount[0]}+{cycleCount[1]}')
            oldCycleCount = cycleCount

        print(
            f'{indent}{input[positions[0]]}',
            *(input[p] for p in positions[1:cycleLength]),
            sep=sep,
        )

if __name__ == '__main__':
    printResults('actagcta')
    # time complexity: 24
    # space complexity: 4
    # a
    # act (cta)
    printResults('abacbadcbdcd')
    # time complexity: 72
    # space complexity: 8
    # ab
    # bc
    # cd
    # bac (acb)
    # -abc (dominated by bac)
    # cbd (bdc)
    # -bcd (dominated by cbd)
    printResults('abcabcac')
    # time complexity: 27
    # space complexity: 4
    # ac *3+0
    # abc *2+1
    printResults('abcdcabdabc')
    # time complexity: 64
    # space complexity: 7
    # ab *3+0
    # abd *2+2
    # abdc *2+0
    printResults('abdcadbcadad')
    # time complexity: 88
    # space complexity: 10
    # ad *4+0
    # adc *2+2
    # -abc *2+1 (dominated by adc)
    # bcad *2+0
    # bdad *2+0
    # -adad *2+0 (eliminated due to subcycle)
    printResults('abcacacabc')
    # ac *4+0
    # abc *2+0
    # aca *2+0
    # cac *2+0
    # -acac *2+0 (eliminated due to subcycle)
    # TODO: remove aca and cac because they are a subsequence of acac
    # but somehow keep abc
    # edit: maybe keeping abc is not that important
    printResults('abdecafbcadbcaebfc')
    # TODO: keep adefc and remove abcabc
    # this should be harder than the previous example because adefc will be
    # dominated at the "merge with existing node" step rather than the
    # "add to result" step
    # edit: never mind, this example produces
    # abcafc
    # adcafc
    # adcabc
    # which dominate adefc anyway.

