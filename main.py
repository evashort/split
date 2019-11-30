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
    stopStack = []
    for start, group in groupby(allSlices, lambda x: x[0]):
        group = list(group)
        stop = start + group[-1][1]
        while stopStack and stop > stopStack[-1]:
            stopStack.pop()

        prefix = '  ' * len(stopStack) \
            + ' '.join(str(x[2]) for x in group) \
            + ' '
        if not stopStack:
            spaceStart = start
            prefixLength = len(prefix)

        substring = ''.join(tokens[start:stop])
        spaceCount = sum(
            map(len, tokens[spaceStart:start])
        ) + prefixLength - len(prefix)

        line = prefix + ' ' * spaceCount + substring
        print(line)
        stopStack.append(stop)

if __name__ == '__main__':
    with open('counts.txt', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # https://www.sitepoint.com/colors-json-example/
            showBreakdown('colors.json')
