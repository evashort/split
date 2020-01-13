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
