import heapq
from suffix_tree import makeSuffixTree

def getMatchingSlices(text):
    root = makeTreeWithStopSets(text)
    seenStopSets = set()
    fringe = [(-len(root.stops), -0, id(root), root)]
    while fringe:
        count, length, _, node = heapq.heappop(fringe)
        count, length = -count, -length
        if count < 2:
            break

        if node.stops in seenStopSets:
            continue

        yield (
            sorted((stop - length) for stop in node.stops),
            length
        )

        seenStopSets.add(node.stops)
        for child in node.children.values():
            heapq.heappush(
                fringe,
                (
                    -len(child.stops),
                    -(length + len(child.text)),
                    id(child),
                    child
                )
            )

def makeTreeWithStopSets(text):
    root = makeSuffixTree(text)
    for node in depthFirst(root, bottomUp=True):
        if node.children:
            node.stops = frozenset(
                stop - len(child.text) \
                    for child in node.children.values() \
                        for stop in child.stops
            )
        else:
            node.stops = frozenset([len(text)])

    return root

def depthFirst(node, bottomUp=False, sort=False, key=None, reverse=False):
    if not bottomUp:
        yield node

    if sort:
        children = sorted(
            node.children.values(),
            key=key,
            reverse=reverse
        )
    else:
        children = node.children.values()

    for child in children:
        yield from depthFirst(child, bottomUp, sort, key, reverse)

    if bottomUp:
        yield node

if __name__ == '__main__':
    text = '{1: 2, 1: 2, 2: 6}'
    sliceSets = getMatchingSlices(text)
    for starts, length in sliceSets:
        start = starts[0]
        substring = text[start:start + length]
        print('{} █{}█'.format(len(starts), substring))
