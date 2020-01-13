from getScore import getScore

def getStateScore(patternFinder, pattern):
    totalLength = patternFinder.getTotalLength(pattern)
    return getScore(len(pattern), totalLength=totalLength)

def getUpperBound(patternFinder, pattern):
    patterns = appendEach(
        pattern,
        patternFinder.getRepeatedTokens(),
        includeOriginal=True
    )
    cycleCounts = sorted(
        filter(
            patternFinder.enoughCycles,
            map(patternFinder.getCycleCount, patterns)
        ),
        reverse=True
    )
    scores = (
        getScore(cycleLength, cycleCount, extraLength) \
            for cycleLength, (cycleCount, extraLength) \
                in enumerate(cycleCounts, start=len(pattern))
    )
    return max(scores)

def getChildren(patternFinder, pattern):
    children = appendEach(
        pattern,
        patternFinder.getRepeatedTokens()
    )
    filteredChildren= (
        list(child) for child in children \
            if patternFinder.enoughCycles(
                patternFinder.getCycleCount(child)
            )
    )
    return filteredChildren

def appendEach(items, lastItemChoices, includeOriginal=False):
    if includeOriginal:
        yield items

    itemsPlus = items + [None]
    for lastItem in lastItemChoices:
        itemsPlus[-1] = lastItem
        yield itemsPlus
