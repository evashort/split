import numpy as np
from imageio import imwrite
from pathlib import Path

testCaseFolder = Path('testcases')
imageFolder = Path('images')
imageFolder.mkdir(exist_ok=True)

for testCase in [
    'WhoisRIR.java',
    'colors.json',
    'RSVPAgent.log',
    'colors2.json'
]:
    print(testCase)
    with open(testCaseFolder / testCase, 'rb') as f:
        text = f.read(5000)

    tokens = np.frombuffer(text, dtype=np.byte)
    costs = np.full(
        (len(tokens), len(tokens)),
        float('inf')
    )
    costs[:, 0] = 0
    for y in range(1, len(tokens)):
        for x in range(y):
            costs[y, x + 1] = min(
                costs[y, x],
                costs[y - 1, x + 1],
                costs[y - 1, x]
            ) + (
                tokens[x] != tokens[y]
            ) / (
                x - y + len(tokens)
            )

    result = np.zeros((len(tokens), len(tokens)), dtype=np.uint8)

    y = len(tokens) - 1
    x = np.argmin(costs[-1, 1:])
    while x > 0:
        result[y, x] = 255
        if costs[y, x] <= costs[y - 1, x + 1]:
            if costs[y - 1, x] <= costs[y, x]:
                x -= 1
                y -= 1
            else:
                x -= 1
        else:
            if costs[y - 1, x] <= costs[y - 1, x + 1]:
                x -= 1
                y -= 1
            else:
                y -= 1

    imwrite(
        imageFolder / (testCase + '.dtw.png'),
        result[::-1]
    )
