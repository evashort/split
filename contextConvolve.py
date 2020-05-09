import numpy as np
from matplotlib import pyplot as plt
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

def maxSmear(swatches, decayRatio=0.6, initialBlend=0):
    blend = initialBlend
    for swatch in swatches:
        yield blend
        blend = max(blend, swatch)
        blend *= decayRatio

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

    return np.fromiter(
        maxSmear(scores, decayRatio=smearDecayRatio),
        dtype=float,
        count=len(scores)
    )

startTime = time.time()
beforeScores = getScores(tokens, selectionStart - 1)
afterScores = getScores(tokens[::-1], len(tokens) - 1 - selectionStop)[::-1]
scores = beforeScores * afterScores
duration = time.time() - startTime
print(f'getting scores took {duration:.2f}s')
plt.bar(nonSequenceIndices, scores[nonSequenceIndices])
plt.bar(sequenceIndices, scores[sequenceIndices])
plt.show()
