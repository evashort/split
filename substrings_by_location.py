import bisect

class SubstringsByLocation:
    def __init__(self, substrings):
        '''
        substrings: a list of (starts, length) pairs
        '''
        self.substrings = substrings
        self.startIDs = sorted(
            (start, i) \
                for i, (starts, _) in enumerate(self.substrings) \
                    for start in starts
        )

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
                    if self.substrings[i][1] <= stopIndex - i
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
