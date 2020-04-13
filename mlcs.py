import bisect
import collections
import heapq
import itertools
import nonDominated
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
        ): {
            # path
            (token,): [
                (
                    float('inf'), # partialStart
                    0 # partialLength
                )
            ] # partials
        } \
            for token in tokenPositions
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
        pathPartials = keyPaths.pop(key)
        if cycleCount < prevCycleCount:
            if prevCycleCount < float('inf'):
                result.sort(
                    key=lambda item: item[4], # partialLength
                    reverse=True
                )
                for item in result:
                    if not hasSubcycle(item[0]):
                        yield getPathPositions(*item[:4], tokenPositions)

            minPathLength = 1 + max(
                len(path) for path, *_ in result
            ) \
                if result else minPathLength
            result = []
            prevCycleCount = cycleCount

        nonOverlappingRanges = list(nonOverlapping(cycleRanges))
        pathItems = (
            (
                path,
                firstStop,
                nonOverlappingRanges,
                partialStart,
                partialLength
            ) \
                for path, partials in pathPartials.items() \
                    for partialStart, partialLength in partials \
                        if partialStart >= nonOverlappingRanges[-1][-1] \
                            and len(path) >= minPathLength
        )
        result = nonDominated.nonDominated(
            list(pathItems),
            key=lambda item: (
                len(item[0]), # cycleLength
                item[4] # partialLength
            ),
            existing=result
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
                newPartialLength = max(map(len, pathPartials))
                newPartials = [(lastStart, newPartialLength)]
            else:
                newPartialLength = 0

            newPathPartials = {
                path + (childToken,): (
                    partials + newPartials \
                        if len(path) == newPartialLength \
                            else partials
                ) \
                    for path, partials in pathPartials.items()
            }

            childKey = (
                -childCycleCount,
                childFirstStop,
                childCycleRanges
            )
            try:
                existingPathPartials = keyPaths[childKey]
            except KeyError:
                childPathPartials = newPathPartials
                heapq.heappush(fringe, childKey)
            else:
                childItems = nonDominated.nonDominated(
                    list(flatItems(newPathPartials)),
                    key=lambda item: (
                        len(item[0]), # cycleLength
                        item[1][0], # partialStart
                        item[1][1], # partialLength
                    ),
                    existing=list(flatItems(existingPathPartials))
                )
                childPathPartials = multiDict(childItems)

            keyPaths[childKey] = childPathPartials

    result.sort(
        key=lambda item: item[4], # partialLength
        reverse=True
    )
    for item in result:
        if not hasSubcycle(item[0]):
            yield getPathPositions(*item[:4], tokenPositions)

    print(f'time complexity: {keysConsidered}')
    print(f'space complexity: {maxDAGLength}')

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

