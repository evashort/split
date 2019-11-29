from itertools import tee
from substrings_by_location import SubstringsByLocation

def getSeparatorPairs(substrings):
    '''
    substrings: list of (starts, length) pairs
    '''
    finder = SubstringsByLocation(substrings)
    for i, (starts, length) in enumerate(substrings):
        gapSubstrings = [
            multiDict(finder.idsInInterval(*gap)) \
                for gap in getGaps(starts, length)
        ]
        allIDs = set(
            j \
                for substrings in gapSubstrings \
                    for j, start in substrings
        )
        gapStartsBySubstringPair = (
            (
                (i, j),
                [
                    substrings.get(j, []) \
                        for substrings in gapSubstrings
                ]
            ) \
                for j in allIDs
        )
        yield from gapStartsBySubstringPair

def getGaps(starts, length):
    preStarts, gapStops = tee(starts)
    gapStarts = (
        preStart + length for preStart in preStarts
    )
    next(gapStops)
    return zip(gapStarts, gapStops)

def multiDict(items):
    result = {}
    for k, v in items:
        result.setdefault(k, []).append(v)

    return result

def scoreSeparatorPair(gapStarts):
    return sum(
        1 for starts in gapStarts \
            if len(starts) == 1
    ) \
        / len(gapStarts)
