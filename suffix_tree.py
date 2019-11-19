from collections import deque
# implementation of Ukkonen's algorithm for constructing a suffix tree in
# linear time.
#
# I used this StackOverflow page for reference, but the way I implemented it is
# somewhat different.
# https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english/9513423
#
# This visualization is great for debugging:
# https://brenden.github.io/ukkonen-animation/

class Node:
    def __init__(self, text):
        self.text = text # text on the edge between this node and its parent
        self.children = {}
        self.popCache = None # suffix link

    def __getitem__(self, branch):
        return self.children[branch]

    def __setitem__(self, branch, newChild):
        self.children[branch] = newChild

    def __repr__(self):
        return ',\n'.join([
            'text=\'{}\''.format(self.text),
            'branches={{{}{}}}'.format(
                ','.join(
                    '\n    \'{}\': \'{}\'{}{}'.format(
                        branch,
                        child.text,
                        ('cache' if child.popCache is not None else ''),
                        ('...' if child.children else '')
                    ) \
                        for branch, child in sorted(
                            self.children.items()
                        )
                ),
                '\n' if self.children else ''
            ),
            'cache={}'.format(
                None if self.popCache is None else '(\n    {}\n)'.format(
                    '{}'.format(self.popCache).replace('\n', '\n    ')
                )
            )
        ])

def makeSuffixTree(text):
    root = Node(text[:0])
    path = Path(root)
    for i in range(len(text) + 1):
        suffix = text[i:]
        lastNewNode = None
        while True:
            try:
                firstLetter = suffix[0]
            except IndexError:
                firstLetter = None

            try:
                path.append(firstLetter)
            except KeyError:
                pass
            else:
                break

            newNode = path.fork()
            newNode[firstLetter] = Node(suffix)
            if lastNewNode is not None:
                lastNewNode.popCache = newNode

            if path:
                path.popleft()
            else:
                break

            lastNewNode = newNode

    return root

class Path:
    '''
    Represents a location in the suffix tree, specified by a sequence of
    letters.
    '''
    def __init__(self, root):
        self.root = root
        self.node = root # last node on path
        self.nodeDepth = 0 # depth of last node on path
        self.letters = deque()

    def append(self, letter):
        '''
        Append a letter to the path. If the resulting path no longer refers to
        a real location in the tree, the change will be reverted and KeyError
        will be raised.
        '''
        self.letters.append(letter)
        try:
            self.normalize()
        except KeyError:
            self.letters.pop()
            raise

    def fork(self):
        '''
        Return a node at the current path location. This may be an existing
        node or a new node created by splitting an edge.
        '''
        try:
            branch = self.letters[self.nodeDepth]
        except IndexError:
            return self.node

        nextNode = self.node[branch]

        splitIndex = len(self.letters) - self.nodeDepth
        newNode = Node(nextNode.text[:splitIndex])
        self.node[branch] = newNode
        self.node = newNode
        self.nodeDepth += splitIndex

        nextNode.text = nextNode.text[splitIndex:]
        self.node[nextNode.text[0]] = nextNode
        return self.node

    def popleft(self):
        '''
        Remove the first letter from the path.
        '''
        self.letters.popleft()
        if self.node.popCache is not None:
            self.node = self.node.popCache
            self.nodeDepth -= 1
        else:
            self.node = self.root
            self.nodeDepth = 0

        self.normalize()

    def __len__(self):
        return len(self.letters)

    def normalize(self):
        '''
        Enforce the invariant that self.node is the last node on the path
        specified by self.letters.

        More specifically, enforce the following 3 invariants:
        1. self.nodeDepth is the distance from self.root to self.node
        2. self.nodeDepth <= len(self.letters)
        3. If self.nodeDepth < len(self.letters),
            then len(self.letters) < (depth of nextNode),
            where nextNode is the child of self.node such that
            nextNode.text matches self.letters

        Preconditions:
        1. self.nodeDepth is the distance from self.root to self.node
        2. self.nodeDepth <= len(self.letters)
        3. self.node is on the path specified by self.letters
        4. self.letters refers to an existing location on the tree

        Note: If the final letter in the path is not in the tree, KeyError will
        be raised. If other letters are not in the tree, the behavior is
        undefined.
        '''
        nextNode = self.node
        nextNodeDepth = self.nodeDepth
        while nextNodeDepth < len(self.letters):
            self.node = nextNode
            self.nodeDepth = nextNodeDepth

            branch = self.letters[self.nodeDepth]
            nextNode = self.node[branch]
            nextNodeDepth = self.nodeDepth + len(nextNode.text)

        if self.letters:
            # don't let append() add a letter that's not in the tree
            pathLastLetter = self.letters[-1]
            treeLastLetter = nextNode.text[
                len(self.letters) - 1 - self.nodeDepth
            ]
            if pathLastLetter != treeLastLetter:
                raise KeyError(pathLastLetter)

        if nextNodeDepth == len(self.letters):
            self.node = nextNode
            self.nodeDepth = nextNodeDepth

if __name__ == '__main__':
    x = makeSuffixTree('abcabxabcd')
    print(x)
