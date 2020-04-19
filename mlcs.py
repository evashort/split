import bisect
import collections
import heapq
import itertools
import time

def getBestRepeatedPaths(sequence, minCycleCount=2):
    tokenPositions = {}
    for position, token in enumerate(sequence):
        tokenPositions.setdefault(token, []).append(position)

    result = []
    resultCycleCount = len(sequence) + 1
    resultScore = (
        0, # pathLength
        0 # partialLength
    )
    for cycleCount, shape, path in getAllRepeatedPaths(
        tokenPositions,
        minCycleCount=minCycleCount
    ):
        if cycleCount < resultCycleCount:
            if result:
                resultScore = (
                    resultScore[0] + 1, # pathLength
                    0 # partialLength
                )

            yield from processResult(result, tokenPositions)
            result.clear()
            resultCycleCount = cycleCount

        partialLength = sum(
            1 for _ in chooseIncreasing(
                (tokenPositions[token] for token in path),
                start=shape[-1][1] # lastStop
            )
        )
        score = (len(path), partialLength)
        if score >= resultScore:
            if score > resultScore:
                result.clear()
                resultScore = score

            result.append(path)

    yield from processResult(result, tokenPositions)

def processResult(paths, tokenPositions):
    for path in paths:
        if not hasSubcycle(path):
            yield path, list(
                chooseIncreasing(
                    itertools.cycle(
                        tokenPositions[token] for token in path
                    )
                )
            )

def hasSubcycle(sequence):
    for cycleLength in range(1, len(sequence) // 2 + 1):
        if len(sequence) % cycleLength == 0 and all(
            sequence[i] == sequence[j] \
                for i in range(cycleLength) \
                    for j in range(
                        i + cycleLength,
                        len(sequence),
                        cycleLength
                    )
        ):
            return True

    return False

def getAllRepeatedPaths(tokenPositions, minCycleCount=2):
    shapePaths = {
        getShape([positions]): [(token,)] \
            for token, positions in tokenPositions.items()
    }
    fringe = [
        (
            -countNonOverlapping(shape), # cycleCount (negative)
            -getWingspan(shape), # wingspan (negative)
            shape
        ) \
            for shape in shapePaths
    ]
    heapq.heapify(fringe)
    shapeHeads = {}
    shapeTails = {}
    while fringe:
        key = heapq.heappop(fringe)
        cycleCount, _, shape = key
        cycleCount = -cycleCount
        paths = shapePaths.pop(shape)
        for path in paths:
            yield cycleCount, shape, path
            prefixShape = getShape(
                tokenPositions[token] for token in path[:-1]
            )
            suffixShape = getShape(
                tokenPositions[token] for token in path[1:]
            )
            childPathsWithShapes = itertools.chain(
                (
                    (
                        (head,) + path,
                        addHead(shape, tokenPositions[head])
                    ) \
                        for head in shapeHeads.get(prefixShape, [])
                ),
                (
                    (
                        path + (tail,),
                        addTail(shape, tokenPositions[tail])
                    ) \
                        for tail in shapeTails.get(suffixShape, [])
                ),
                [
                    (
                        path + (path[0],),
                        addTail(shape, tokenPositions[path[0]])
                    )
                ] \
                    if all(token == path[0] for token in path) \
                        else []
            )
            for childPath, childShape in childPathsWithShapes:
                childCycleCount = countNonOverlapping(childShape)
                if childCycleCount < minCycleCount:
                    continue

                existingPaths = shapePaths.setdefault(childShape, [])
                if existingPaths:
                    existingPathLength = len(existingPaths[0])
                    if len(childPath) > existingPathLength:
                        existingPaths.clear()

                    if len(childPath) >= existingPathLength:
                        existingPaths.append(childPath)
                else:
                    childKey = (
                        -countNonOverlapping(childShape),
                        -getWingspan(childShape),
                        childShape
                    )
                    assert childKey > key
                    heapq.heappush(fringe, childKey)
                    existingPaths.append(childPath)

            shapeTails.setdefault(prefixShape, set()).add(path[-1])
            shapeHeads.setdefault(suffixShape, set()).add(path[0])

def getCycleCount(path, tokenPositions):
    totalLength = sum(
        1 for _ in chooseIncreasing(
            path,
            itertools.cycle(
                tokenPositions[token] for token in path
            )
        )
    )
    return divmod(totalLength, len(path))

def chooseIncreasing(menus, start=0):
    choice = start - 1
    for menu in menus:
        choiceIndex = bisect.bisect_left(menu, choice + 1)
        try:
            choice = menu[choiceIndex]
        except IndexError:
            break

        yield choice

def getWingspan(shape):
    '''
    wingspan = lastStart - firstStop
    this quantity is useful because it is guaranteed to decrease every time a
    new head or tail is added to shape
    '''
    return shape[-1][0] - shape[0][1]

def countNonOverlapping(ranges):
    return sum(1 for _ in nonOverlapping(ranges))

def nonOverlapping(ranges):
    lastStop = float('-inf') # pylint: disable=unused-variable
    return (
        (start, lastStop := stop)
            for start, stop in ranges \
                if start >= lastStop
    )

def getShape(menus):
    shape = None
    for menu in menus:
        if shape is None:
            shape = tuple(
                (position, position + 1) for position in menu
            )
        else:
            shape = addTail(shape, menu)

        if not shape:
            break

    return shape

def addHead(ranges, positions):
    ranges = iter(ranges)
    positions = iter(positions)
    lastPosition = -1
    result = []
    while True:
        for start, stop in ranges:
            if start > lastPosition:
                break
        else:
            break

        for position in positions:
            if position >= start:
                break

            lastPosition = position
        else:
            if lastPosition >= 0:
                result.append((lastPosition, stop))

            break

        if lastPosition >= 0:
            result.append((lastPosition, stop))

        lastPosition = position

    return tuple(result)

assert addHead(
    ((1, 3), (3, 5), (4, 6)),
    [0, 1, 2, 10]
) == \
    ((0, 3), (2, 5))

assert addHead(((1, 3),), [0]) == ((0, 3),)

assert addHead(((1, 3),), [1]) == ()

def addTail(ranges, positions):
    ranges = iter(ranges)
    positions = iter(positions)
    lastStop = -1
    result = []
    while True:
        for position in positions:
            if position >= lastStop:
                break
        else:
            break

        for start, stop in ranges:
            if stop > position:
                break

            lastStart, lastStop = start, stop
        else:
            if lastStop >= 0:
                result.append((lastStart, position + 1))

            break

        if lastStop >= 0:
            result.append((lastStart, position + 1))

        lastStart, lastStop = start, stop

    return tuple(result)

assert addTail(
    ((1, 3), (2, 4), (4, 6)),
    [4, 5, 6, 10]
) == \
    ((2, 5), (4, 7))

assert addTail(((1, 3),), [3]) == ((1, 4),)

assert addTail(((1, 3),), [2]) == ()

def printResults(input, sep='', indent='    ', minCycleCount=2):
    if len(input) < 80:
        print()
        print(input)

    results = getBestRepeatedPaths(input, minCycleCount=minCycleCount)
    oldCycleCount = (0, 0)
    lastTime = time.time()
    for path, positions in results:
        cycleCount = divmod(len(positions), len(path))
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
            f'{indent}{path[0]}',
            *path[1:],
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

