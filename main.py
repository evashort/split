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
    for starts, length in sorted(
        sliceSets,
        key=lambda item: len(item[0]) * item[1],
        reverse=True
    ):
        start = starts[0]
        print('{} █{}█'.format(
            len(starts),
            ''.join(tokens[start : start + length])
        ))

if __name__ == '__main__':
    with open('counts.txt', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # https://www.sitepoint.com/colors-json-example/
            showCounts('colors.json')
