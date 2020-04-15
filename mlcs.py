import bisect
import collections
import heapq
import itertools
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
        ): (
            1, # pathLength
            [
                (
                    len(sequence), # partialStart
                    0 # partialLength
                )
            ], # partials
            [
                (
                    (token, None), # path
                    {len(sequence)}, # partialStart
                )
            ] # pathPartialStarts
        ) \
            for token in tokenPositions
    }
    fringe = list(keyPaths)
    heapq.heapify(fringe)

    maxDAGLength = 1
    keysConsidered = 0

    result = []
    resultCycleCount = float('inf')
    resultPathLength = 0
    resultPartialLength = 0
    while fringe:
        maxDAGLength = max(maxDAGLength, len(fringe))

        key = heapq.heappop(fringe)
        cycleCount, firstStop, cycleRanges = key
        cycleCount = -cycleCount
        pathLength, partials, pathPartialStarts = keyPaths.pop(key)

        if cycleCount < resultCycleCount:
            yield from processResult(result, tokenPositions)
            resultCycleCount = cycleCount
            if result:
                resultPathLength += 1
                resultPartialLength = 0

            result.clear()

        if pathLength >= resultPathLength:
            if pathLength > resultPathLength:
                result.clear()
                resultPathLength = pathLength
                resultPartialLength = 0

            nonOverlappingRanges = list(nonOverlapping(cycleRanges))
            lastStop = nonOverlappingRanges[-1][1]
            partialIndex = bisect.bisect_left(partials, (lastStop, 0))
            partialStart, partialLength = partials[partialIndex]
            if partialLength >= resultPartialLength:
                if partialLength > resultPartialLength:
                    result.clear()
                    resultPartialLength = partialLength

                allowedPartialStarts = {partialStart}
                # add all later starts that have the same length
                # (note that partials are ordered by increasing start
                # which is equivalent to decreasing length)
                for i in range(partialIndex + 1, len(partials)):
                    partialStart, partialLength = partials[i]
                    if partialLength < resultPartialLength:
                        break

                    allowedPartialStarts.add(partialStart)

                result.extend(
                    # len(partialStarts) will be 1 because the same path can't
                    # have two partialStarts with the same partialLength
                    (
                        path,
                        firstStop,
                        nonOverlappingRanges,
                        *partialStarts
                    ) \
                        for path, partialStarts in filterPathPartialStarts(
                            pathPartialStarts,
                            allowedPartialStarts
                        )
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

            childKey = (
                -childCycleCount,
                childFirstStop,
                childCycleRanges
            )
            otherPathLength = 0
            try:
                otherPathLength, otherPartials, otherPathPartialStarts \
                    = keyPaths[childKey]
            except KeyError:
                heapq.heappush(fringe, childKey)

            childPathLength = pathLength + 1
            if childPathLength < otherPathLength:
                continue

            # if lastStart is gone, it must have become partial
            lastStart = cycleRanges[-1][0]
            if childCycleRanges[-1][0] < lastStart:
                childPartials = [(lastStart, pathLength)] + partials
                newPartialStarts = {lastStart}
                childPathPartialStarts = [
                    (
                        (childToken, path),
                        partialStarts.union(newPartialStarts)
                    ) \
                        for path, partialStarts in pathPartialStarts
                ]
            else:
                childPartials = partials
                childPathPartialStarts = [
                    ((childToken, path), partialStarts) \
                        for path, partialStarts in pathPartialStarts
                ]

            if otherPathLength == childPathLength:
                childPartials, childPathPartialStarts = mergePartialMappings(
                    (childPartials, childPathPartialStarts),
                    (otherPartials, otherPathPartialStarts)
                )

            keyPaths[childKey] = (
                childPathLength,
                childPartials,
                childPathPartialStarts
            )

    yield from processResult(result, tokenPositions)

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

def mergePartialMappings(*partialMappings):
    mergedPartials = getNonDominatedPartials(
        {
            partial \
                for partials, _ in partialMappings \
                    for partial in partials
        }
    )
    partialSet = set(mergedPartials)
    mergedPathPartialStarts = [
        pair \
            for filteredPathPartialStarts in (
                filterPathPartialStarts(
                    pathPartialStarts,
                    {start for start, _ in partialSet.intersection(partials)}
                ) \
                    for partials, pathPartialStarts in partialMappings
            ) \
                for pair in filteredPathPartialStarts
    ]
    return mergedPartials, mergedPathPartialStarts

def getNonDominatedPartials(partials):
    '''
    For each value of start, choose the partial with the maximum length
    unless there is a partial with a later start and a greater length.
    '''
    # sort by decreasing start, then decreasing length
    partials = sorted(partials, reverse=True)
    # force lengths to be increasing
    minLengths = itertools.accumulate(
        (length for _, length in partials),
        max
    )
    nonDominatedPartials = [
        partial for partial, minLength in zip(partials, minLengths) \
            if partial[1] == minLength
    ]
    nonDominatedPartials.reverse()
    return nonDominatedPartials

def filterPathPartialStarts(pathPartialStarts, allowedPartialStarts):
    return (
        (filteredPath, filteredPartialStarts) \
            for filteredPath, filteredPartialStarts in (
                # I believe set intersection is faster if the smaller
                # set is passed in as other
                (path, allowedPartialStarts.intersection(partialStarts)) \
                    for path, partialStarts in pathPartialStarts
            ) \
                if filteredPartialStarts
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
    menus = [tokenPositions[token] for token in path]

    result = list(
        chooseDecreasing(reversed(menus), firstStop - 1)
    )
    result.reverse()

    for cycleStart, _ in cycleRanges:
        result.extend(chooseIncreasing(menus, cycleStart))

    if partialStart <= menus[0][-1]:
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

def processResult(result, tokenPositions):
    for nestedPath, *rest in result:
        path = []
        while nestedPath is not None:
            token, nestedPath = nestedPath
            path.append(token)

        path.reverse()
        if not hasSubcycle(path):
            yield getPathPositions(path, *rest, tokenPositions)

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
    # -abd *2+2 (shorter than abdc)
    # abdc *2+0
    printResults('abdcadbcadad')
    # time complexity: 88
    # space complexity: 10
    # ad *4+0
    # -adc *2+2 (shorter than bcad)
    # -abc *2+1 (dominated by adc)
    # bcad *2+0
    # bdad *2+0
    # -adad *2+0 (eliminated due to subcycle)
    printResults('abcacacabc')
    # ac *4+0
    # -abc *2+0
    # -aca *2+0
    # -cac *2+0
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

