import numpy as np
from matplotlib import pyplot as plt
import suffix_tree

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

def smear(swatches, decayRatio=0.6, initialBlend=1):
    blend = initialBlend
    for swatch in swatches:
        yield blend
        blend += swatch
        blend *= decayRatio

def getPositions(children, textLength):
    if children:
        for child in children.values():
            for stop in getPositions(child.children, textLength):
                yield stop - len(child.text)
    else:
        yield textLength

def getScores(tokens, start, decayRatio=0.6, minWeight=0.01):
    scores = np.zeros(len(tokens))
    weight = 1
    root = suffix_tree.makeSuffixTree(tokens)
    for pathStart in range(start, len(tokens)):
        node = root
        pathLength = 0
        while node.children:
            token = tokens[pathStart + pathLength]
            node = node.children[token]
            pathLength += len(node.text)

            for position in getPositions(node.children, len(text)):
                scores[position - pathLength] += weight * pathLength

        weight *= decayRatio
        if weight < minWeight:
            break

    scores = np.fromiter(
        smear(scores[::-1], decayRatio=decayRatio),
        dtype=float,
        count=len(text)
    )
    return scores[::-1]

beforeScores = getScores(tokens[::-1], len(tokens) - selectionStart)[::-1]
afterScores = getScores(tokens, selectionStop)
scores = beforeScores * afterScores
plt.bar(nonSequenceIndices, scores[nonSequenceIndices])
plt.bar(sequenceIndices, scores[sequenceIndices])
plt.show()
