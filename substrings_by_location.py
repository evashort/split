import bisect

class SubstringsByLocation:
    def __init__(self, substrings):
        '''
        substrings: iterable of (starts, length) pairs
        '''
        self.lengths = []
        self.startIDs = []
        for i, (starts, length) in enumerate(substrings):
            self.lengths.append(length)
            self.startIDs.extend(
                (start, i) for start in starts
            )

        self.startIDs.sort()

    def idsInInterval(self, start, stop):
        '''
        returns (id, location) pairs for substrings
        of the string text[start:stop]
        '''
        startIndex = bisect.bisect_left(self.startIDs, (start,))
        stopIndex = bisect.bisect_left(self.startIDs, (stop,))
        return (
            (i, start) \
                for start, i in self.startIDs[startIndex:stopIndex] \
                    if self.lengths[i] <= stopIndex - i
        )

if __name__ == '__main__':
    finder = SubstringsByLocation([
        ([-2], 2) # 0: fully outside left
        ([0], 2) # 1: outside left
        ([1], 2) # 2: spans exactly
        ([2], 2) # 3: outside right
        ([4], 7) # 4: fully outside right
        ([-2, 0, 1, 2, 4], 2) # 5: all of the above
        ([0], 4) #6: outside both
    ])
    print(finder.idsInInterval(1, 3)) # [(2, 1), (5, 1)]
