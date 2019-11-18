from suffix_tree import makeSuffixTree

def getSubstringCounts(text):
    global root
    root = makeTreeWithStopSets(text)
    substringCounts = {}
    seenStopSets = set()
    getSubstringCountsHelp(root, seenStopSets, substringCounts, '')
    return substringCounts

def getSubstringCountsHelp(node, seenStopSets, substringCounts, prefix):
    for child in node.children.values():
        if child.children and child.stops not in seenStopSets:
            seenStopSets.add(child.stops)
            substring = prefix + child.text
            substringCounts[substring] = len(child.stops)
            getSubstringCountsHelp(
                child,
                seenStopSets,
                substringCounts,
                substring
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
    substringCounts = getSubstringCounts(
        '{1: 2, 1: 2, 2: 6}'
    )
    for substring, count in sorted(
        substringCounts.items(),
        key=lambda item: item[1]
    ):
        print('{} █{}█'.format(count, substring))
