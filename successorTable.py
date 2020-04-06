import bisect
from typing import Dict, Hashable, Iterable, List, Set, Tuple, TypeVar

Token = TypeVar('Token')
class SuccessorTable:
    def __init__(self, sequence: Iterable[Token], alphabet: Set[Token]):
        self.tokenPositions = multidict(
            (token, position) \
                for position, token in enumerate(sequence) \
                    if token in alphabet
        )

    def index(self, token: Token, start: int=0):
        try:
            positions = self.tokenPositions[token]
        except KeyError:
            raise ValueError(f'token not found: {token}')

        positionIndex = bisect.bisect_left(positions, start)
        try:
            position = positions[positionIndex]
        except IndexError:
            return float('inf')

        return position

    def rindex(self, token: Token, end: int=float('inf')):
        try:
            positions = self.tokenPositions[token]
        except KeyError:
            raise ValueError(f'token not found: {token}')

        positionIndex = bisect.bisect_right(positions, end) - 1
        try:
            position = positions[positionIndex]
        except IndexError:
            raise ValueError(
                f'token not found in range [0, {end}]: {token}'
            )

        return position

Key = TypeVar('Key', bound=Hashable)
Value = TypeVar('Value')
def multidict(items: Iterable[Tuple[Key, Value]]) -> Dict[Key, List[Value]]:
    result = {}
    for k, v in items:
        result.setdefault(k, []).append(v)

    return result
