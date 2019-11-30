from contextlib import redirect_stdout
from itertools import groupby
from most_common_substrings import \
    makeTreeWithStopSets, getMatchingSlices
from pathlib import Path
from preprocessor import preprocess
import re

def showBreakdown(testCase):
    with open(Path('testcases') / testCase) as f:
        text = f.read()

    tokens = preprocess(text)
    tree = makeTreeWithStopSets(tokens)
    sliceSets = getMatchingSlices(tree)
    allSlices = sorted(
        (start, length, i, len(starts)) \
            for i, (starts, length) in enumerate(sliceSets) \
                for start in starts
    )
    stopStack = [float('inf')]
    for start, group in groupby(allSlices, lambda x: x[0]):
        group = list(group)
        stop = start + group[-1][1]
        while stop > stopStack[-1]:
            stopStack.pop()

        print('{}{} {}'.format(
            '    ' * (len(stopStack) - 1),
            ' '.join(str(x[2]) for x in group),
            ''.join(tokens[start:stop])
        ))
        stopStack.append(stop)

if __name__ == '__main__':
    with open('counts.txt', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # https://www.sitepoint.com/colors-json-example/
            showBreakdown('colors.json')
