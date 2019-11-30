from contextlib import redirect_stdout
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
        (start, -length, i, len(starts)) \
            for i, (starts, length) in enumerate(sliceSets) \
                for start in starts
    )
    for start, length, i, count in allSlices:
        length = -length
        print('{}{} {}'.format(
            ' ' * getIndentLevel(count),
            i,
            ''.join(tokens[start : start + length])
        ))

def getIndentLevel(count):
    if count >= 12:
        return 0
    if count >= 5:
        return 4
    elif count >= 3:
        return 8
    else:
        return 12

if __name__ == '__main__':
    with open('counts.txt', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # https://www.sitepoint.com/colors-json-example/
            showBreakdown('colors.json')
