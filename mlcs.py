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
    for cycleCount, partialLength, path in getAllRepeatedPaths(
        tokenPositions,
        minCycleCount=minCycleCount
    ):
        if cycleCount < resultCycleCount:
            for oldPath in result:
                if not hasSubcycle(oldPath):
                    yield oldPath, list(
                        getPathPositions(oldPath, tokenPositions)
                    )

            result.clear()
            resultCycleCount = cycleCount
            resultScore = (
                resultScore[0] + 1, # pathLength
                0 # partialLength
            )

        score = (len(path), partialLength)
        if score >= resultScore:
            if score > resultScore:
                result.clear()
                resultScore = score

            result.append(path)

    for path in result:
        if not hasSubcycle(path):
            yield path, list(
                getPathPositions(path, tokenPositions)
            )

def getAllRepeatedPaths(tokenPositions, minCycleCount=2):
    fringe = [
        (
            -len(positions), # cycleCount (negative)
            1, # pathLength
            0, # partialLength
            (token,) # path
        ) \
            for token, positions in tokenPositions.items()
    ]
    heapq.heapify(fringe)
    bodyHeads = {}
    bodyTails = {}
    while fringe:
        key = heapq.heappop(fringe)
        cycleCount, _, partialLength, path = key
        cycleCount = -cycleCount
        yield cycleCount, partialLength, path
        prefix, suffix = path[:-1], path[1:]
        childPaths = itertools.chain(
            (
                (head,) + path for head in bodyHeads.get(prefix, [])
            ),
            (
                path + (tail,) for tail in bodyTails.get(suffix, [])
            ),
            [path + (path[0],)] \
                if all(token == path[0] for token in suffix) \
                    else []
        )
        for childPath in childPaths:
            childCycleCount, childPartialLength = getCycleCount(
                childPath,
                tokenPositions
            )
            if childCycleCount >= minCycleCount:
                childKey = (
                    -childCycleCount,
                    len(childPath),
                    childPartialLength,
                    childPath
                )
                assert childKey > key
                heapq.heappush(fringe, childKey)

        bodyTails.setdefault(prefix, []).append(path[-1])
        bodyHeads.setdefault(suffix, []).append(path[0])

def getCycleCount(path, tokenPositions):
    totalLength = sum(
        1 for _ in getPathPositions(path, tokenPositions)
    )
    return divmod(totalLength, len(path))

def getPathPositions(path, tokenPositions):
    position = -1
    for token in itertools.cycle(path):
        positionIndex = bisect.bisect_left(
            tokenPositions[token],
            position + 1
        )
        try:
            position = tokenPositions[token][positionIndex]
        except IndexError:
            break

        yield position

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

