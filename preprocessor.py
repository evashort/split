import numpy as np

def preprocess(text):
    tokenList = list(tokenize(text))
    return np.asarray(tokenList, dtype=object)

def tokenize(text):
    tokenLength = 1
    tokenType = 'other'
    for i, letter in enumerate(text):
        oldTokenType = tokenType
        if letter.isalnum() or not letter.isascii():
            tokenType = 'word'
        elif letter.isspace():
            tokenType = 'space'
        else:
            tokenType = 'other'

        if tokenType == oldTokenType == 'word':
            tokenLength += 1
        elif oldTokenType == 'word':
            yield text[i - tokenLength : i].lower()

        if tokenType == oldTokenType == 'space':
            tokenLength += 1

        if tokenType == 'other':
            yield letter

        if tokenType != oldTokenType:
            tokenLength = 1

    if tokenType == 'word':
        yield text[-tokenLength:].lower()

if __name__ == '__main__':
    print(list(tokenize('a,~  1bA  \tC')))
