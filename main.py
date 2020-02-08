import preprocessor
from mlcs import mlcs

if __name__ == '__main__':
    with open('testcases/colors.json') as f:
        text = f.read()
    tokens = [
        token for i, token in preprocessor.tokenize(text)
    ]
    result = mlcs(tokens, 18)
    for sequence in result:
        print(sequence)
        print(f'sequence length: {len(sequence)}')
    # time complexity: 97112
    # space complexity: 19444
    # sequence length: 101
