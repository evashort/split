import preprocessor
from mlcs import mlcs

if __name__ == '__main__':
    with open('testcases/colors.json') as f:
        text = f.read()
    tokens = [
        token for i, token in preprocessor.tokenize(text)
    ]
    results = mlcs(tokens)
    for cycleCount, result in results:
        print(cycleCount)
        print(*result, sep='\n')
    # time complexity: 110595198
    # space complexity: 487550
