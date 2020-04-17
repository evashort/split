import preprocessor
import mlcs

if __name__ == '__main__':
    with open('testcases/colors.json') as f:
        text = f.read()
    tokens = [
        token for i, token in preprocessor.tokenize(text)
    ]
    mlcs.printResults(tokens)
    # time complexity: 110595198
    # space complexity: 487550
