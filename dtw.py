import bisect
import numpy as np
from imageio import imwrite
from pathlib import Path
import time
import parentFinderLib
import yFinderLib

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
    startTime = time.time()
    yFinder = yFinderLib.YFinder(tokens)
    p = -1
    offsetScores = [
        offset ** p if offset else 0.0 \
            for offset in range(yFinder.maxOffset + 1)
    ]

    planes = []
    parentFinder = parentFinderLib.ParentFinder([(0, 0, 0.0)])
    for outerX, token in enumerate(tokens):
        while yFinder.hasY(outerX):
            plane = []
            x, y = outerX, len(tokens)
            while x < y:
                if yFinder.hasY(x) and yFinder.peekY(x) < y:
                    y = yFinder.popY(x)
                    _, _, parentScore = parentFinder.getBestParent(x, y)
                    plane.append(
                        (x, y, parentScore + offsetScores[y - x])
                    )

                x += 1

            planes.append(plane)
            parentFinder.__init__(plane)

    path = []
    x, y = len(tokens), len(tokens)
    for plane in reversed(planes):
        parentFinder.__init__(plane)
        x, y, _ = parentFinder.getBestParent(x, y)
        path.append((x, y))

    path.reverse()
    duration = time.time() - startTime
    print(f'{testCase} took {duration:.2f}s')

    result = np.zeros((len(tokens), len(tokens), 3), dtype=np.uint8)
    for x, y in path:
       result[y, x] = 255
    for plane in planes:
        for x, y, score in plane:
            hue = (score % 100) / 100
            if hue < 1/6:
                red = 1
                green = 6 * hue
                blue = 0
            elif hue < 1/3:
                red = 6 * (1/3 - hue)
                green = 1
                blue = 0
            elif hue < 1/2:
                red = 0
                green = 1
                blue = 6 * (hue - 1/3)
            elif hue < 2/3:
                red = 0
                green = 6 * (2/3 - hue)
                blue = 1
            elif hue < 5/6:
                red = 6 * (hue - 2/3)
                green = 0
                blue = 1
            else:
                red = 1
                green = 0
                blue = 6 * (1 - hue)

            red, green, blue = (
                int(np.clip(channel * 255, 0, 255)) \
                    for channel in (red, green, blue)
            )

            result[y, x] = (red, green, blue)

    imwrite(
        imageFolder / (testCase + '.dtw.png'),
        result[::-1]
    )
