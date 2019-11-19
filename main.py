from contextlib import redirect_stdout
from most_common_substrings import getSubstringCounts
from pathlib import Path
from preprocessor import preprocess
import re

def showCounts(testCase):
    with open(Path('testcases') / testCase) as f:
        text = f.read()

    tokens = preprocess(text)
    substringCounts = getSubstringCounts(tokens)
    for substring, count in sorted(
        substringCounts.items(),
        key=lambda item: item[1] * len(item[0]),
        reverse=True
    ):
        print('{} █{}█'.format(count, re.escape(substring).replace(r'\ ', r'[\s\n]+')))

if __name__ == '__main__':
    with open('counts.txt', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # https://www.sitepoint.com/colors-json-example/
            showCounts('colors.json')
