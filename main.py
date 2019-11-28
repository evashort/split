from contextlib import redirect_stdout
from most_common_substrings import getSubstringCounts
from pathlib import Path
from preprocessor import preprocess
import re

def showCounts(testCase):
    with open(Path('testcases') / testCase) as f:
        text = f.read()

    tokens = preprocess(text)
    sliceSets = getMatchingSlices(tokens)
    for sliceSet in sorted(
        sliceSets,
        key=lambda slices: \
            len(slices) * (slices[0][1] - slices[0][0]),
        reverse=True
    ):
        (start, stop), *_ = sliceSet
        print('{} █{}█'.format(
            len(sliceSet),
            ''.join(tokens[start:stop])
        ))

if __name__ == '__main__':
    with open('counts.txt', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # https://www.sitepoint.com/colors-json-example/
            showCounts('colors.json')
