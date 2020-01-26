from referenceCounter import ReferenceCounter
from successorTable import SuccessorTable

def mlcs(*sequences):
    # https://www.frontiersin.org/articles/10.3389/fgene.2017.00104/full
    alphabet = set.intersection(*map(set, sequences))
    tables = [
        SuccessorTable(sequence, alphabet) for sequence in sequences
    ]
    initialKey = (-1,) * len(sequences)
    leveledDAG = {initialKey: Node()}
    parentCounts = ReferenceCounter({initialKey: 0})
    fringe = [initialKey]
    result = []
    while leveledDAG:
        newFringe = []
        for key in fringe:
            node = leveledDAG[key]
            for childToken in alphabet:
                try:
                    childKey = tuple(
                        table.index(childToken, position + 1) \
                            for position, table in zip(key, tables)
                    )
                except ValueError:
                    continue

                node.children.append(childKey)
                parentCounts.add(childKey)
                if childKey not in leveledDAG:
                    leveledDAG[childKey] = Node()
                    newFringe.append(childKey)

        fringe = newFringe

        for key in parentCounts.getGarbage():
            node = leveledDAG.pop(key)
            if key[0] >= 0:
                token = sequences[0][key[0]]
                childPaths = [path + [token] for path in node.paths]
            else:
                childPaths = [[]]

            for childKey in node.children:
                parentCounts.remove(childKey)
                childNode = leveledDAG[childKey]
                childNode.paths = keepLongest(childNode.paths, childPaths)

            if not node.children:
                result = keepLongest(result, childPaths)

    return result

def keepLongest(*pathLists):
    maxLength = max(
        len(paths[0]) for paths in filter(pathLists)
    )
    result = []
    for paths in filter(pathLists):
        if len(paths[0]) == maxLength:
            result += paths

    return result

class Node:
    def __init__(self):
        self.children = []
        self.paths = []

if __name__ == '__main__':
    print(*mlcs('actagcta', 'tcaggtat'), sep='\n')
    # tagta
    # cagta
