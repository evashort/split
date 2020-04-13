import bisect
import collections
import heapq
import itertools
from nds2D import NDS2D
import time

def mlcs(sequence, minCycleCount=2):
    tokenCounts = collections.Counter(sequence)
    tokenPositions = {}
    for position, token in enumerate(sequence):
        if tokenCounts[token] >= minCycleCount:
            tokenPositions.setdefault(token, []).append(position)

    # Invariants:
    # -key.cycleCount <= -key.child.cycleCount
    # key.firstCycleStop < key.child.firstCycleStop
    # Consequently, key < key.child
    # Therefore by the time a key is popped from the heap,
    # all its parents have already been expanded.
    keyPaths = {
        (
            -len(tokenPositions[token]), # cycleCount (negative)
            tokenPositions[token][0] + 1, # firstCycleStop
            tuple(
                (p, p + 1) for p in tokenPositions[token][1:]
            ), # cycleRanges
        ): [
            (
                (token, None), # path
                1, # cycleLength (pathLength)
                [
                    (
                        0, # partialLength
                        float('inf') # partialStart
                    )
                ] # partials
            )
         ] \
            for token in tokenPositions
    }
    fringe = list(keyPaths)
    heapq.heapify(fringe)
    maxDAGLength = 1
    keysConsidered = 0
    prevCycleCount = float('inf')
    minPathLength = 1
    result = []
    resultScores = set()
    nds2D = NDS2D()
    while fringe:
        maxDAGLength = max(maxDAGLength, len(fringe))
        key = heapq.heappop(fringe)
        cycleCount, firstStop, cycleRanges = key
        cycleCount = -cycleCount
        pathPartials = keyPaths.pop(key)
        if cycleCount < prevCycleCount:
            if prevCycleCount < float('inf'):
                result = sorted(
                    (item for item in result if item[0] in resultScores),
                    key=lambda item: item[0]
                )
                for item in result:
                    yield getPathPositions(*item[1:], tokenPositions)

            minPathLength = 1 + max(
                (pathLength for (pathLength, _), *_ in result),
                default=minPathLength - 1
            )
            result.clear()
            resultScores.clear()
            prevCycleCount = cycleCount

        nonOverlappingRanges = list(nonOverlapping(cycleRanges))
        *_, (_, lastStop) = nonOverlappingRanges
        filteredPathPartials = [
            (
                path,
                pathLength,
                max(
                    (
                        partial for partial in partials \
                            if partial[1] >= lastStop
                    ),
                    default=(0, 0)
                )
            ) \
                for path, pathLength, partials in pathPartials \
                    if pathLength >= minPathLength \
                        and not hasSubcycle(unlinkList(path))
        ]
        resultScores.update(
            (pathLength, partialLength) \
                for _, pathLength, (partialLength, _) in filteredPathPartials
        )
        resultScores = set(nonDominated2D(resultScores))
        result.extend(
            (
                (pathLength, partialLength),
                path,
                firstStop,
                nonOverlappingRanges,
                partialStart
            ) for (
                path,
                pathLength,
                (partialLength, partialStart)
            ) in filteredPathPartials \
                if (pathLength, partialLength) in resultScores
        )

        for childToken in tokenPositions:
            keysConsidered += 1

            childFirstStop, childCycleRanges = getChildCycleRanges(
                firstStop,
                cycleRanges,
                tokenPositions[childToken]
            )

            childCycleCount = 1 + sum(
                1 for i in nonOverlapping(childCycleRanges)
            )
            if childCycleCount < minCycleCount:
                continue

            # if lastStart is gone, it must have become partial
            lastStart = cycleRanges[-1][0]
            if childCycleRanges[-1][0] < lastStart:
                newPartialLength = max(
                    pathLength for _, pathLength, _ in pathPartials
                )
                newPartials = [(newPartialLength, lastStart)]
            else:
                newPartialLength = 0

            childPathPartials = [
                (
                    (childToken, path),
                    1 + pathLength,
                    partials + newPartials \
                        if pathLength == newPartialLength \
                            else partials
                ) \
                    for path, pathLength, partials in pathPartials
            ]

            childKey = (
                -childCycleCount,
                childFirstStop,
                childCycleRanges
            )
            try:
                existingPathPartials = keyPaths[childKey]
            except KeyError:
                heapq.heappush(fringe, childKey)
            else:
                childPathPartials.extend(existingPathPartials)
                triples = sorted(
                    {
                        (pathLength, *partial) \
                            for _, pathLength, partials in childPathPartials \
                                for partial in partials
                    },
                    reverse=True
                )
                triples = {
                    triple for triple in triples \
                        if nds2D.add((-triple[1], -triple[2]))
                }
                nds2D.clear()
                childPathPartials = (
                    (
                        path,
                        pathLength,
                        [
                            partial for partial in partials \
                                if (pathLength, *partial) in triples
                        ]
                    ) \
                        for path, pathLength, partials in childPathPartials
                )
                childPathPartials = [
                    pathPartial for pathPartial in childPathPartials \
                        if pathPartial[2] # partials
                ]

            keyPaths[childKey] = childPathPartials

    result = sorted(
        (item for item in result if item[0] in resultScores),
        key=lambda item: item[0]
    )
    for item in result:
        yield getPathPositions(*item[1:], tokenPositions)

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

def nonDominated2D(items):
    items = sorted(
        items,
        key=lambda item: item[::-1],
        reverse=True
    )
    stairs = itertools.accumulate(items, max)
    return (
        item for item, par in zip(items, stairs) \
            if item == par
    )

def multiDict(items):
    result = {}
    for k, v in items:
        result.setdefault(k, []).append(v)

    return result

def flatItems(multiDict):
    return (
        (key, value) \
            for key, values in multiDict.items() \
                for value in values
    )

def getChildCycleRanges(firstStop, cycleRanges, tokenPositions):
    if firstStop > tokenPositions[-1]:
        return float('inf'), ()

    childFirstStop = 1 + tokenPositions[
        bisect.bisect_left(tokenPositions, firstStop)
    ]

    # extend each range by including the next occurrence of
    # childToken, removing any ranges that overlap the first range
    extendedRanges = (
        (
            start,
            1 + tokenPositions[
                bisect.bisect_left(tokenPositions, stop)
            ]
        ) \
            for start, stop in cycleRanges \
                if start >= childFirstStop and stop <= tokenPositions[-1]
    )

    # remove dominated ranges by picking the latest start for each
    # distinct value of stop
    nonDominatedRanges = tuple(
        lastRange \
            for _, (*_, lastRange) in itertools.groupby(
                extendedRanges,
                lambda range: range[1]
            )
    )

    return childFirstStop, nonDominatedRanges

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
    tokenPositions
):
    path = unlinkList(path)
    menus = [tokenPositions[token] for token in path]

    result = list(
        chooseDecreasing(reversed(menus), firstStop - 1)
    )
    result.reverse()

    for cycleStart, _ in cycleRanges:
        result.extend(chooseIncreasing(menus, cycleStart))

    if partialStart < float('inf'):
        result.extend(chooseIncreasing(menus, partialStart))

    return len(path), result

def chooseIncreasing(menus, firstChoice):
    menus = iter(menus)
    next(menus)
    yield (choice := firstChoice)
    for choices in menus:
        i = bisect.bisect_right(choices, choice)
        if i >= len(choices):
            break

        yield (choice := choices[i])

def chooseDecreasing(menus, firstChoice):
    menus = iter(menus)
    next(menus)
    yield (choice := firstChoice)
    for choices in menus:
        i = bisect.bisect_left(choices, choice) - 1
        if i < 0:
            break

        yield (choice := choices[i])

def unlinkList(linkedList):
    result = []
    while linkedList is not None:
        item, linkedList = linkedList
        result.append(item)

    result.reverse()
    return result

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
    lastTime = time.time()
    for cycleLength, positions in results:
        cycleCount = divmod(len(positions), cycleLength)
        if len(input) > 80 and cycleCount[0] != oldCycleCount[0]:
            thisTime = time.time()
            duration = thisTime - lastTime
            lastTime = thisTime
        else:
            duration = 0

        if cycleCount != oldCycleCount:
            thisTime = time.time()
            if duration:
                print(
                    f'*{cycleCount[0]}+{cycleCount[1]}' \
                        f'                {duration}'
                )
            else:
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

