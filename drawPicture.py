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
    with open(testCaseFolder / testCase, 'rb') as f:
        text = f.read(5000)

    tokens = np.frombuffer(text, dtype=np.byte)
    imwrite(
        imageFolder / (testCase + '.png'),
        (tokens == tokens[:, None]).astype(float)[::-1]
    )
