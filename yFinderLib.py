class YFinder:
    def __init__(self, tokens):
        tokenPositions = {}
        for position, token in enumerate(tokens):
            tokenPositions.setdefault(token, []).append(position)

        yCount = len(tokens) - len(tokenPositions)
        self.yIndices = [0] * len(tokens)
        self.allYs = [] # length = yCount
        for positions in sorted(
            tokenPositions.values(),
            key=secondOrZero,
            reverse=True
        ):
            positions = iter(positions)
            for x in positions: # pylint: disable=unused-variable
                break
            else:
                continue

            for y in positions:
                self.yIndices[x] = len(self.allYs)
                self.allYs.append(y)
                x = y

            self.yIndices[x] = yCount

    def hasY(self, x):
        return self.yIndices[x] < len(self.allYs)

    def peekY(self, x):
        return self.allYs[self.yIndices[x]]

    def popY(self, x):
        yIndex = self.yIndices[x]
        y = self.allYs[yIndex]
        yIndex += 1
        if yIndex < len(self.allYs) and self.allYs[yIndex] < y:
            yIndex = len(self.allYs)

        self.yIndices[x] = yIndex
        return y

def secondOrZero(items):
    if len(items) < 2:
        return 0

    return items[1]

if __name__ == '__main__':
    #                  012345
    yFinder = YFinder('abacba')
    assert yFinder.allYs == [4, 2, 5]
    assert yFinder.yIndices == [1, 0, 2, 3, 3, 3]
