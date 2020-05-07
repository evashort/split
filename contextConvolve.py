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

def multiplyScores(
    tokens,
    scores,
    tokenWeights,
    decayRatio=0.6,
    initialScore=1
):
    score = initialScore
    for i, token in enumerate(tokens):
        scores[i] *= score
        score *= decayRatio
        score += tokenWeights.get(token, 0)

beforeWeights = getTokenWeights(tokens[selectionStart - 1::-1])
afterWeights = getTokenWeights(tokens[selectionStop:])
scores = np.ones_like(tokens, dtype=float)
multiplyScores(tokens, scores, beforeWeights)
multiplyScores(tokens[::-1], scores[::-1], afterWeights)
plt.bar(nonSequenceIndices, scores[nonSequenceIndices])
plt.bar(sequenceIndices, scores[sequenceIndices])
plt.show()
