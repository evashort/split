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

def getAllRepeatedPaths(tokenPositions, sequence, minCycleCount=2):
    alphabet = {
        token for token, positions in tokenPositions.items() \
            if len(positions) >= minCycleCount
    }
    shapePaths = {None: [()]}
    fringe = [
        (
            -(len(sequence) + 1), # cycleCount (negative)
            False, # generateLowerCycleCounts
            None # shape
        )
    ]
    while fringe:
        key = heapq.heappop(fringe)
        cycleCount, generateLowerCycleCounts, shape = key
        cycleCount = -cycleCount
        if generateLowerCycleCounts or cycleCount == minCycleCount:
            paths = shapePaths.pop(shape)
        else:
            paths = shapePaths[shape]
            peerKey = (
                -cycleCount,
                True, # generateLowerCycleCounts
                shape
            )
            assert peerKey > key
            heapq.heappush(fringe, peerKey)

        if generateLowerCycleCounts:
            yield cycleCount - 1, (), ()
            tails = alphabet.difference(
                getTailsWithSameCycleCount(shape, sequence)
            )
        else:
            for path in paths:
                yield cycleCount, shape, path

            tails = getTailsWithSameCycleCount(shape, sequence)

        childPathLength = len(paths[0]) + 1
        for tail in tails:
            childShape = addTail(shape, tokenPositions[tail])
            if generateLowerCycleCounts:
                if len(childShape) < minCycleCount:
                    continue

                childCycleCount = countNonOverlapping(childShape)
                if childCycleCount < minCycleCount:
                    continue
            else:
                childCycleCount = cycleCount

            existingPaths = shapePaths.setdefault(childShape, [])
            if existingPaths:
                existingPathLength = len(existingPaths[0])
                if childPathLength > existingPathLength:
                    existingPaths.clear()
            else:
                childKey = (
                    -childCycleCount,
                    False, # generateLowerCycleCounts
                    childShape
                )
                # TODO: fix the bug and uncomment this assertion
                # assert childKey > key
                heapq.heappush(fringe, childKey)
                existingPathLength = 0

            if childPathLength >= existingPathLength:
                existingPaths.extend(
                    path + (tail,) \
                        for path in paths
                )

def chooseIncreasing(menus, start=0):
    choice = start - 1
    for menu in menus:
        choiceIndex = bisect.bisect_left(menu, choice + 1)
        try:
            choice = menu[choiceIndex]
        except IndexError:
            break

        yield choice

def countNonOverlapping(ranges):
    return sum(1 for _ in nonOverlapping(ranges))

def nonOverlapping(ranges):
    lastStop = float('-inf') # pylint: disable=unused-variable
    return (
        (start, lastStop := stop)
            for start, stop in ranges \
                if start >= lastStop
    )

def getTailsWithSameCycleCount(shape, sequence):
    if shape is None:
        return set()

    # if shape == ((0, 13), (14, 22), (16, 24), (19, 26), (21, 29), (23, 31), (25, 33), (28, 35), (30, 38), (32, 40), (34, 44), (37, 46), (39, 59), (43, 61), (45, 63), (58, 66), (60, 75), (62, 77), (65, 79), (74, 81), (76, 84), (78, 86), (80, 88), (83, 90), (85, 93), (87, 95), (89, 99), (92, 101), (94, 114), (98, 116), (100, 118), (113, 121), (115, 130), (117, 132), (120, 134), (129, 136), (131, 139), (133, 141), (135, 143), (138, 145), (140, 148), (142, 150), (144, 152), (147, 154), (149, 157), (151, 159), (153, 163), (156, 165), (158, 178), (162, 180), (164, 182), (177, 185), (179, 194), (181, 196), (184, 198), (193, 200), (195, 203), (197, 205), (199, 207), (202, 209), (204, 212), (206, 214), (208, 216), (211, 218), (213, 221), (215, 223), (217, 227), (220, 229), (222, 242), (226, 244), (228, 246), (241, 249), (243, 258), (245, 260), (248, 262), (257, 264), (259, 267), (261, 269), (263, 271), (266, 273), (268, 276), (270, 278), (272, 280), (275, 282), (277, 285), (279, 287), (281, 291), (284, 293), (286, 306), (290, 308), (292, 310), (305, 313), (307, 322), (309, 324), (312, 326), (321, 328), (323, 331), (325, 333), (327, 335), (330, 337), (332, 340), (334, 342), (336, 344), (339, 346), (341, 349), (343, 351), (345, 355), (348, 357), (350, 370), (354, 372), (356, 374), (369, 377)):
    #     print("this shape produces {':'} but it should produce {':', '↵'}")

    ranges = nonOverlapping(shape)
    result = set()
    for _, lastStop in ranges:
        break
    else:
        return result

    for start, stop in ranges:
        if result:
            result.intersection_update(sequence[lastStop:start])
        else:
            result.update(sequence[lastStop:start])

        if not result:
            return result

        lastStop = stop

    if result:
        result.intersection_update(sequence[lastStop:])
    else:
        result.update(sequence[lastStop:])

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
