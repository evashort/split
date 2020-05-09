import numpy as np
from matplotlib import pyplot as plt
import time

with open('./testcases/colors.json', 'rb') as f:
    text = f.read()

def rangeFromStartAndLength(start, length):
    return range(start, start + length)

sequence = [b'black', b'white', b'red', b'blue', b'yellowisabeautifulbrightcolor', b'green']
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
    smearDecayRatio=0.999
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

    blend = 0
    for i, score in enumerate(scores):
        if score > blend:
            blend = score
        else:
            scores[i] = blend

        blend *= smearDecayRatio

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
scores = beforeScores * afterScores
duration = time.time() - startTime
print(f'getting scores took {duration:.2f}s')
peaks = sorted(getPeaks(scores), reverse=True)
for score, peakStart, peakStop in peaks:
    print(score, text[peakStart + 1 : peakStop - 1].decode('utf-8'))

plt.bar(nonSequenceIndices, scores[nonSequenceIndices])
plt.bar(sequenceIndices, scores[sequenceIndices])
plt.show()
