from itertools import tee
from substrings_by_location import SubstringsByLocation

def getSeparatorPairs(substrings):
    '''
    substrings: list of (starts, length) pairs
    '''
    finder = SubstringsByLocation(substrings)
    for i, (starts, length) in enumerate(substrings):
        perGapIDStarts = [
            multiDict(finder.idsInInterval(*gap)) \
                for gap in getGaps(starts, length)
        ]
        allIDs = set(
            j \
                for idStarts in perGapIDStarts \
                    for j in idStarts
        )
        yield from (
            (
                (i, j),
                [
                    idStarts.get(j, []) \
                        for idStarts in perGapIDStarts
                ]
            ) \
                for j in allIDs
        )

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
