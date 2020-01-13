import heapq

def aStar(getCost, getBound, getChildren, initialStates, maximize=False):
    sign = -1 if maximize else 1

    fringe = [
        (sign * getBound(state), state) \
            for state in initialStates
    ]
    heapq.heapify(fringe)

    pendingResults = []
    while fringe:
        lowerBound, state = heapq.heappop(fringe)

        cost = sign * getCost(state)
        if cost < lowerBound:
            raise AssertionError(
                f'cost < lowerBound ({cost} < {lowerBound})\n'
                f'state =\n'
                f'{indent(repr(state))}'
            )

        heapq.heappush(pendingResults, (cost, state))

        while pendingResults and pendingResults[0][0] <= lowerBound:
            betterCost, betterState = heapq.heappop(pendingResults)
            yield sign * betterCost, betterState

        for child in getChildren(state):
            childBound = sign * getBound(child)
            if childBound < lowerBound:
                raise AssertionError(
                    f'childBound < lowerBound ({childBound} < {lowerBound})\n'
                    f'child =\n'
                    f'{indent(repr(child))}\n'
                    f'state =\n'
                    f'{indent(repr(state))}'
                )

            heapq.heappush(fringe, (childBound, child))

    while pendingResults:
        cost, state = heapq.heappop(pendingResults)
        yield sign * cost, state

def indent(text, spaces=4):
    lines = text.split('\n')
    return '\n'.join(
        (' ' * spaces + line if line else line) \
            for line in lines
    )
