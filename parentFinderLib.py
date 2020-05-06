class ParentFinder:
    def __init__(self, plane):
        '''
        plane: a list of (x, y, score) triples sorted by increasing x
            and also decreasing y
        '''
        self.plane = plane
        self.start, self.stop = 0, 0

    def getBestParent(self, x, y):
        while self.stop < len(self.plane) \
            and self.plane[self.stop][0] <= x:
            self.stop += 1

        while self.start < len(self.plane) \
            and self.plane[self.start][1] > y:
            self.start += 1

        return max(
            self.plane[self.start:self.stop],
            key=lambda item: item[2]
        )
