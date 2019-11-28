from itertools import tee
from substrings_by_location import SubstringsByLocation

def getSeparatorPairs(substrings):
    '''
    substrings: list of (starts, length) pairs
    '''
    finder = SubstringsByLocation(substrings)
    for i, (starts, length) in enumerate(substrings):
        idStartSets =
        for gap in getGaps(starts, length):
            for j, start = dict(finder.idsInInterval(*gap))
            for 
            
def getGaps(starts, length):
    preStarts, gapStops = tee(starts)
    gapStarts = (
        preStart + length for preStart in preStarts
    )
    next(gapStops)
    return zip(gapStarts, gapStops)
