import preprocessor
import mlcs
import time

if __name__ == '__main__':
    with open('testcases/colors.json') as f:
        text = f.read()
    sequence = [
        token for i, token in preprocessor.tokenize(text)
    ]
    minCycleCount = 6
    tokenPositions = {}
    for position, token in enumerate(sequence):
        tokenPositions.setdefault(token, []).append(position)

    tokenPositions = {
        token: positions \
            for token, positions in tokenPositions.items() \
                if len(positions) >= minCycleCount
    }
    startTime = time.time()
    for cycleCount, shape, path in mlcs.getAllRepeatedPaths(
        tokenPositions,
        sequence,
        minCycleCount=minCycleCount
    ):
        if ''.join(path) == '↵{↵"color":"",↵"category":"",↵"code":{↵"rgba":[,,,1],↵"hex":"#"↵}↵},':
            break

    print(time.time() - startTime)
