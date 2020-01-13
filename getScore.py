def getScore(
    cycleLength, cycleCount=None, extraLength=None, totalLength=None
):
    if totalLength is not None and areNone(cycleCount, extraLength):
        cycleCount = totalLength / cycleLength
    elif cycleCount is not None and isNone(totalLength):
        extraLength = extraLength or 0
        totalLength = cycleCount * cycleLength + extraLength
        cycleCount += extraLength / cycleLength
    elif cycleCount is not None and totalLength is not None:
        raise ValueError('both cycleCount and totalLength were specified')
    elif areNone(cycleCount, extraLength):
        raise ValueError('neither cycleCount nor totalLength was specified')
    else:
        raise ValueError('both totalLength and extraCount were specified')

    return totalLength

def areNone(*args):
    return all(map(isNone, args))

def isNone(x):
    return x is None
