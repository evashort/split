from getScore import getScore

def getStateScore(patternFinder, pattern):
    totalLength = patternFinder.getTotalLength(pattern)
    return getScore(len(pattern), totalLength=totalLength)

def getUpperBound(patternFinder, pattern):
    cycleCounts = [
        patternFinder.getCycleCount(pattern)
    ]
    patternPlus = list(pattern)
    for token in patternFinder.getRepeatedTokens():
        del patternPlus[len(pattern):]
        while True:
            patternPlus.append(token)
            cycleCount = patternFinder.getCycleCount(patternPlus)
            if patternFinder.enoughCycles(cycleCount):
                cycleCounts.append(cycleCount)
            else:
                break

    cycleCounts.sort(reverse=True)

    scores = (
        getScore(cycleLength, cycleCount, extraLength) \
            for cycleLength, (cycleCount, extraLength) \
                in enumerate(cycleCounts, start=len(pattern))
    )
    return max(scores)

def getChildren(patternFinder, pattern):
    patternPlus = pattern + [None]
    for token in patternFinder.getRepeatedTokens():
        patternPlus[-1] = token
        cycleCount = patternFinder.getCycleCount(patternPlus)
        if patternFinder.enoughCycles(cycleCount):
            yield pattern + [token]
