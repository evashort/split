from functools import partial
import genericAStar
from patternFinder import PatternFinder
import stateLib

tokens = 'abcddabcadbcdabca'
#         abc  abca bc abca
#         abcd abc d   abc

patternFinder = PatternFinder(tokens)

results = genericAStar.aStar(
    partial(stateLib.getStateScore, patternFinder),
    partial(stateLib.getUpperBound, patternFinder),
    partial(stateLib.getChildren, patternFinder),
    initialStates=stateLib.getChildren(patternFinder, []),
    maximize=True
)

for result in results:
    print(result)
