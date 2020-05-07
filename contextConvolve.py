import numpy as np
from matplotlib import pyplot as plt

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

def getTokenWeights(tokens, decayRatio=0.6, minWeight=0.01):
    weight = 1
    tokenWeights = {}
    for token in tokens:
        tokenWeights[token] = tokenWeights.get(token, 0) + weight
        weight *= decayRatio
        if weight < minWeight:
            break

    return tokenWeights

def smear(swatches, decayRatio=0.6, initialBlend=1):
    blend = initialBlend
    for swatch in swatches:
        yield blend
        blend += swatch
        blend *= decayRatio

beforeWeights = getTokenWeights(tokens[selectionStart - 1::-1])
afterWeights = getTokenWeights(tokens[selectionStop:])
beforeScores = np.fromiter(
    smear(
        beforeWeights.get(token, 0) for token in tokens
    ),
    dtype=float,
    count=len(tokens)
)
afterScores = np.fromiter(
    smear(
        afterWeights.get(token, 0) for token in tokens[::-1]
    ),
    dtype=float,
    count=len(tokens)
)[::-1]
scores = beforeScores * afterScores
plt.bar(nonSequenceIndices, scores[nonSequenceIndices])
plt.bar(sequenceIndices, scores[sequenceIndices])
plt.show()
