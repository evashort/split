import bisect
import numpy as np
from imageio import imwrite
from pathlib import Path
import time
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

    planes = []
    for outerX, token in enumerate(tokens):
        while yFinder.hasY(outerX):
            plane = []
            x, y = outerX, len(tokens)
            while x < y:
                if yFinder.hasY(x) and yFinder.peekY(x) < y:
                    y = yFinder.popY(x)
                    plane.append((x, y))

                x += 1

            planes.append(plane)

    path = []
    x, y = 0, 0
    for plane in reversed(planes):
        firstBadIndex = bisect.bisect_right(plane, (x, float('inf')))
        x, y = plane[firstBadIndex - 1]
        path.append((x, y))

    path.reverse()
    duration = time.time() - startTime
    print(f'{testCase} took {duration:.2f}s')

    result = np.zeros((len(tokens), len(tokens), 3), dtype=np.uint8)
    for x, y in path:
       result[y, x] = 255
    # for i, plane in enumerate(planes):
    #     hue = (i % 100) / 100
    #     if hue < 1/6:
    #         red = 1
    #         green = 6 * hue
    #         blue = 0
    #     elif hue < 1/3:
    #         red = 6 * (1/3 - hue)
    #         green = 1
    #         blue = 0
    #     elif hue < 1/2:
    #         red = 0
    #         green = 1
    #         blue = 6 * (hue - 1/3)
    #     elif hue < 2/3:
    #         red = 0
    #         green = 6 * (2/3 - hue)
    #         blue = 1
    #     elif hue < 5/6:
    #         red = 6 * (hue - 2/3)
    #         green = 0
    #         blue = 1
    #     else:
    #         red = 1
    #         green = 0
    #         blue = 6 * (1 - hue)

    #     red, green, blue = (
    #         int(np.clip(channel * 255, 0, 255)) \
    #             for channel in (red, green, blue)
    #     )

    #     for x, y in plane:
    #         result[y, x] = (red, green, blue)

    imwrite(
        imageFolder / (testCase + '.dtw.png'),
        result[::-1]
    )
