def prune(node, minStopCount=2, parentDepth=0):
    depth = parentDepth + len(node.text)
    if not node.children:
        return [depth]

    stops = []
    branchesToPrune = []
    for branch, child in node.children.items():
        childStarts = prune(child, minStopCount, depth)
        if childStarts is not None:
            stops += childStarts
            branchesToPrune.append(branch)

    if len(branchesToPrune) < len(node.children):
        for branch in branchesToPrune:
            del node.children[branch]

    elif len(stops) >= minStopCount:
        node.children.clear()
    else:
        starts = stops
        for i in range(len(starts)):
            starts[i] -= len(node.text)

        return starts

    node.setStops(stops)
    return None

def countDescendants(node):
    return sum(
        1 + countDescendants(child) \
            for child in node.children.values()
    )

if __name__ == '__main__':
    import suffix_tree
    testRoot1 = suffix_tree.makeSuffixTree('abcabxabcd')
    prune(testRoot1, 2)
    assert countDescendants(testRoot1) == 5

    with open('./testcases/colors.json', 'rb') as f:
        text = f.read()

    root = suffix_tree.makeSuffixTree(text)
    prune(root, 6)
    print(countDescendants(root))
