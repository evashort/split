import collections
import numpy as np
import time

with open('./testcases/colors.json', 'rb') as f:
    text = f.read()

def rangeFromStartAndLength(start, length):
    return range(start, start + length)

sequence = [b'black', b'white', b'red', b'blue', b'yellow', b'green']
sequenceIndices = [
    i \
        for item in sequence \
            for i in rangeFromStartAndLength(text.index(item), len(item))
]
nonSequenceIndices = [
    i for i in range(len(text)) if i not in sequenceIndices
]

selectedText = b'black'
selectionStart = text.index(selectedText)
selectionStop = selectionStart + len(selectedText)

tokens = np.frombuffer(text, dtype=np.byte)

def getScores(
    tokens,
    end,
    decayRatio=0.9,
    minWeight=0.05,
    smearDecayRatio=0.95
):
    tokenPositions = {}
    for position, token in enumerate(tokens):
        tokenPositions.setdefault(token, []).append(position)

    scores = np.zeros(len(tokens))
    maxOffset = int(np.log(minWeight) / np.log(decayRatio))
    for offset in range(maxOffset, -1, -1):
        weight = decayRatio ** offset
        assert weight >= minWeight
        token = tokens[end - offset]
        starts = tokenPositions[token]
        for i, start in enumerate(starts):
            try:
                stop = starts[i + 1]
            except IndexError:
                stop = len(tokens)

            blend = scores[start] + weight
            for x in range(start, stop):
                if blend < scores[x] + minWeight:
                    break

                scores[x] = blend
                blend *= decayRatio

    return scores

def getPeaks(sequence, minRatio=0.999):
    try:
        valleyHeight = sequence[0]
    except ValueError:
        return

    i = 0
    while True:
        for i in range(i + 1, len(sequence)):
            if sequence[i] * minRatio > valleyHeight:
                peakHeight = sequence[i]
                break

            valleyHeight = min(valleyHeight, sequence[i])
        else:
            break

        for i in range(i + 1, len(sequence)):
            if sequence[i] < peakHeight * minRatio:
                valleyHeight = sequence[i]
                break

            peakHeight = max(peakHeight, sequence[i])
        else:
            break

        for peakStart in range(i - 1, 0, -1):
            if sequence[peakStart - 1] < peakHeight * minRatio:
                break

        yield peakHeight, peakStart, i

assert list(getPeaks(
    [8, 10, 8, 1, 8, 10, 8, 4, 5, 4, 5, 6, 5, 4, 10],
    #0  1   2  3  4  5   6  7  8  9  10 11 12 13 14
    minRatio=0.8
)) \
    == [(10, 4, 7), (6, 10, 13)]

startTime = time.time()
beforeScores = getScores(tokens, selectionStart - 1)
afterScores = getScores(tokens[::-1], len(tokens) - 1 - selectionStop)[::-1]

decayRatio = 0.9
maxOffset = 29
weightAfterTokens = collections.Counter()
peaks = list(getPeaks(beforeScores))
for peakHeight, _, peakStop in peaks:
    weight = peakHeight
    # https://en.wikipedia.org/wiki/Geometric_series#Formula
    remainingWeight = peakHeight / (1 - decayRatio)
    tokenCounts = collections.Counter()
    for offset in range(maxOffset + 1):
        token = tokens[peakStop - 1 - offset]
        ordinal = tokenCounts[token]
        tokenCounts[token] += 1
        remainingWeight -= weight
        weightAfterTokens[(token, ordinal)] += remainingWeight
        weight *= decayRatio

beforeString = str(bytes(
    byte for (byte, ordinal), weight in sorted(
        weightAfterTokens.items(),
        key=lambda item: item[1]
    )
))
print(beforeString)
