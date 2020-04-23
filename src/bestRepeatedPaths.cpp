#include "bestRepeatedPaths.h"

using namespace std;

bool operator>(const PathScore& lhs, const PathScore& rhs)
{
    if (lhs.pathLength != rhs.pathLength) {
        return lhs.pathLength > rhs.pathLength;
    }
    return lhs.partialLength > rhs.partialLength;
}

bool operator>=(const PathScore& lhs, const PathScore& rhs)
{
    if (lhs.pathLength != rhs.pathLength) {
        return lhs.pathLength > rhs.pathLength;
    }
    return lhs.partialLength >= rhs.partialLength;
}

template<class T>
BestRepeatedPathGenerator<T>::BestRepeatedPathGenerator(
    vector<T> sequence,
    int minCycleCount
) : sequence(sequence),
    generator(
        getTokenPositions(sequence, minCycleCount),
        sequence.size(),
        minCycleCount
    )
{
    stagedCycleCount = sequence.size();
    // skip the empty path by making the current score higher
    stagedScore = PathScore({
        1, // pathLength
        0 // partialLength
    });
}

template<class T>
bool BestRepeatedPathGenerator<T>::hasNext() {
    return stagedCycleCount > 0;
}

template<class T>
vector<RepeatedPath<T> > BestRepeatedPathGenerator<T>::next(int ticks) {
    vector<RepeatedPath<T> > result;
    for (int tick = 0; tick < ticks; tick++) {
        PathInfo<T> pathInfo = generator.next();
        if (pathInfo.cycleCount < stagedCycleCount) {
            if (!stagedPaths.empty()) {
                stagedScore.pathLength += 1;
                stagedScore.partialLength = 0;
            }
            typename vector<vector<T> >::const_iterator stagedPathIter
                = stagedPaths.cbegin();
            for (; stagedPathIter != stagedPaths.cend(); stagedPathIter++) {
                if (!hasSubcycle(*stagedPathIter)) {
                    result.push_back(
                        RepeatedPath<T>({
                            *stagedPathIter,
                            getPathPositions(*stagedPathIter, sequence)
                        })
                    );
                }
            }
            stagedPaths.clear();
            stagedCycleCount = pathInfo.cycleCount;
        }
        if (pathInfo.cycleCount == 0) {
            break;
        }
        PathScore score({
            static_cast<int>(pathInfo.path.size()),
            getPartialLength(
                pathInfo.path,
                sequence,
                pathInfo.shape.back().stop // lastStop
            )
        });
        if (score >= stagedScore) {
            if (score > stagedScore) {
                stagedPaths.clear();
                stagedScore = score;
            }
            stagedPaths.push_back(pathInfo.path);
        }
    }
    return result;
}

// https://stackoverflow.com/a/495056
template class BestRepeatedPathGenerator<char>;
template class BestRepeatedPathGenerator<string>;

template<class T>
map<T, vector<int> > getTokenPositions(
    const vector<T> &sequence,
    int minCycleCount
) {
    map<T, vector<int> > result;
    for (int i = 0; i < sequence.size(); i++) {
        result[sequence[i]].push_back(i);
    }
    typename map<T, vector<int> >::iterator resultIter = result.begin();
    while (resultIter != result.end()) {
        if (resultIter->second.size() < minCycleCount) {
            resultIter = result.erase(resultIter);
            continue;
        }
        resultIter++;
    }
    return result;
}

template<class T>
bool hasSubcycle(const vector<T> &path) {
    int maxCycleLength = path.size() / 2;
    for (int cycleLength = 1; cycleLength <= maxCycleLength; cycleLength++) {
        if (path.size() % cycleLength != 0) {
            continue;
        }
        for (int i = 0; i < path.size(); i++) {
            for (int j = i + cycleLength; j < path.size(); j += cycleLength) {
                if (path[i] != path[j]) {
                    goto nextCycleLength;
                }
            }
        }
        return true;
        nextCycleLength:
        continue; // apparently goto labels must be followed by a statement
    }
    return false;
}

template<class T>
vector<int> getPathPositions(
    const vector<T> &path,
    const vector<T> &sequence
) {
    typename vector<T>::const_iterator pathIter = path.cbegin();
    vector<int> result;
    for (int position = 0; position < sequence.size(); position++) {
        if (sequence[position] == *pathIter) {
            result.push_back(position);
            pathIter++;
            if (pathIter == path.cend()) {
                pathIter = path.cbegin();
            }
        }
    }
    return result;
}

template<class T>
int getPartialLength(
    const vector<T> &path,
    const vector<T> &sequence,
    int lastStop
) {
    int partialLength = 0;
    for (int position = lastStop; position < sequence.size(); position++) {
        if (sequence[position] == path[partialLength]) {
            partialLength++;
        }
    }
    return partialLength;
}
