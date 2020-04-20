import bisect
import collections
import heapq
import itertools
import time

def getBestRepeatedPaths(sequence, minCycleCount=2):
    tokenPositions = {}
    for position, token in enumerate(sequence):
        tokenPositions.setdefault(token, []).append(position)

    tokenPositions = {
        token: positions \
            for token, positions in tokenPositions.items() \
                if len(positions) >= minCycleCount
    }

    result = []
    resultCycleCount = len(sequence) + 1
    resultScore = (
        0, # pathLength
        0 # partialLength
    )
    for cycleCount, shape, path in getAllRepeatedPaths(
        tokenPositions,
        sequence,
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

        if not path:
            continue

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

def chooseIncreasing(menus, start=0):
    choice = start - 1
    for menu in menus:
        choiceIndex = bisect.bisect_left(menu, choice + 1)
        try:
            choice = menu[choiceIndex]
        except IndexError:
            break

        yield choice

def getAllRepeatedPaths(tokenPositions, sequence, minCycleCount=2):
    shapePaths = {None: [()]}
    fringe = [
        (
            -(len(sequence) + 1), # cycleCount (negative)
            None # shape
        )
    ]
    while fringe:
        key = heapq.heappop(fringe)
        cycleCount, shape = key
        cycleCount = -cycleCount
        paths = shapePaths.pop(shape)
        for path in paths:
            yield cycleCount, shape, path

        childPathLength = len(paths[0]) + 1
        for tail, tailPositions in tokenPositions.items():
            childShape = addTail(shape, tailPositions)
            if len(childShape) < minCycleCount:
                continue

            childCycleCount = countNonOverlapping(childShape)
            if childCycleCount < minCycleCount:
                continue

            existingPaths = shapePaths.setdefault(childShape, [])
            if existingPaths:
                existingPathLength = len(existingPaths[0])
                if childPathLength > existingPathLength:
                    existingPaths.clear()
            else:
                childKey = (
                    -childCycleCount,
                    childShape
                )
                assert childKey > key
                heapq.heappush(fringe, childKey)
                existingPathLength = 0

            if childPathLength >= existingPathLength:
                existingPaths.extend(
                    path + (tail,) \
                        for path in paths
                )

def countNonOverlapping(ranges):
    lastStop = 0
    result = 0
    for start, stop in ranges:
        if start >= lastStop:
            result += 1
            lastStop = stop

    return result

def addTail(ranges, positions):
    if ranges is None:
        positionRanges = (
            (position, position + 1) for position in positions
        )
        for _, firstStop in positionRanges:
            return ((0, firstStop), *positionRanges)

        return ()

    ranges = iter(ranges)
    positions = iter(positions)
    for lastStart, lastStop in ranges:
        break
    else:
        return ()

    for position in positions:
        if position >= lastStop:
            break
    else:
        return ()

    result = [(lastStart, position + 1)]
    for lastStart, lastStop in ranges:
        if lastStart > position:
            break
    else:
        return tuple(result)

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
            result.append((lastStart, position + 1))
            break

        result.append((lastStart, position + 1))
        lastStart, lastStop = start, stop

    return tuple(result)

assert addTail(
    ((1, 3), (2, 4), (4, 6)),
    [4, 5, 6, 10]
) == \
    ((1, 5),)
assert addTail(
    ((0, 0), (1, 3), (2, 4), (4, 6)),
    [0, 4, 5, 6, 10]
) == \
    ((0, 1), (2, 5), (4, 7))
assert addTail(((1, 3),), [3]) == ((1, 4),)
assert addTail(((0, 0), (1, 3),), [0, 3]) == ((0, 1), (1, 4))
assert addTail(((1, 3),), [2]) == ()
assert addTail(((0, 0), (1, 3),), [0, 2]) == ((0, 1),)

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
