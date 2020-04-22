#include "repeatedPaths.h"

using namespace std;

bool operator<(const Range& lhs, const Range& rhs)
{
    if (lhs.start != rhs.start) {
        return lhs.start < rhs.start;
    }
    return lhs.stop < rhs.stop;
}

bool operator<(const Key& lhs, const Key& rhs)
{
    // process in order of increasing cycleCount,
    // or decreasing firstStop in case of a tie
    if (lhs.cycleCount != rhs.cycleCount) {
        return lhs.cycleCount < rhs.cycleCount;
    }
    return lhs.shape[0].stop > rhs.shape[0].stop;
}

template <class T>
RepeatedPathGenerator<T>::RepeatedPathGenerator(
    map<T, vector<int> > tokenPositions,
    int sequenceLength,
    int minCycleCount
) : tokenPositions(tokenPositions),
    minCycleCount(minCycleCount)
{
    key.cycleCount = sequenceLength + 1;
    key.shape.reserve(sequenceLength + 1);
    for (int i = 0; i <= sequenceLength; i++) {
        key.shape.push_back({i, i});
    }
    paths.push_back({});
    pathIter = paths.cbegin();
}

template <class T>
PathInfo<T> RepeatedPathGenerator<T>::next() {
    if (pathIter != paths.cend()) {
        vector<T> path = *pathIter;
        pathIter++;
        return PathInfo<T>({
            key.cycleCount,
            key.shape,
            path
        });
    }
    int childPathLength = paths[0].size() + 1;
    typename map<T, std::vector<int> >::const_iterator tailIter
        = tokenPositions.cbegin();
    for (; tailIter != tokenPositions.cend(); tailIter++) {
        T tail = tailIter->first;
        const vector<int> &tailPositions = tailIter->second;
        vector<Range> childShape = addTail(key.shape, tailPositions);
        if (childShape.size() < minCycleCount) {
            continue;
        }
        int childCycleCount = countNonOverlapping(childShape);
        if (childCycleCount < minCycleCount) {
            continue;
        }
        vector<vector<T> > &childPaths = shapePaths[childShape];
        int existingPathLength = 0;
        if (childPaths.empty()) {
            Key childKey({
                childCycleCount,
                childShape
            });
            // parent must have higher priority than child
            assert(childKey < key);
            fringe.emplace(childKey);
        } else {
            existingPathLength = childPaths[0].size();
            if (childPathLength > existingPathLength) {
                childPaths.clear();
            }
        }
        if (childPathLength >= existingPathLength) {
            pathIter = paths.cbegin();
            for (; pathIter != paths.cend(); pathIter++) {
                vector<T> childPath(*pathIter);
                childPath.push_back(tail);
                childPaths.push_back(childPath);
            }
        }
    }
    if (fringe.empty()) {
        return PathInfo<T>({
            0, // cycleCount
            vector<Range>(), // shape
            vector<T>() // path
        });
    }
    key = fringe.top();
    fringe.pop();
    paths = shapePaths[key.shape];
    pathIter = paths.cbegin();
    vector<T> path = *pathIter;
    pathIter++;
    return PathInfo<T>({
        key.cycleCount,
        key.shape,
        path
    });
}

// https://stackoverflow.com/a/495056
template class RepeatedPathGenerator<char>;

int countNonOverlapping(const vector<Range> &ranges) {
    int result = 0;
    int lastStop = 0;
    vector<Range>::const_iterator rangeIter = ranges.cbegin();
    for (; rangeIter != ranges.cend(); rangeIter++) {
        if (rangeIter->start >= lastStop) {
            result++;
            lastStop = rangeIter->stop;
        }
    }
    return result;
}

vector<Range> addTail(
    const vector<Range> &ranges,
    const vector<int> &positions
) {
    vector<Range> result;
    vector<Range>::const_iterator rangeIter = ranges.cbegin();
    if (rangeIter == ranges.cend()) {
        return result;
    }
    vector<int>::const_iterator positionIter = positions.cbegin();
    for (; positionIter != positions.cend(); positionIter++) {
        if (*positionIter >= rangeIter->stop) {
            break;
        }
    }
    if (positionIter == positions.cend()) {
        return result;
    }
    result.reserve(ranges.size());
    result.push_back({rangeIter->start, *positionIter + 1});
    for (; rangeIter != ranges.cend(); rangeIter++) {
        if (rangeIter->start > *positionIter) {
            break;
        }
    }
    while (rangeIter != ranges.cend()) {
        for (; positionIter != positions.cend(); positionIter++) {
            if (*positionIter >= rangeIter->stop) {
                break;
            }
        }
        if (positionIter == positions.cend()) {
            break;
        }
        int lastStart = rangeIter->start;
        for (; rangeIter != ranges.cend(); rangeIter++) {
            if (rangeIter->start > *positionIter) {
                break;
            }

            lastStart = rangeIter->start;
        }
        result.push_back({lastStart, *positionIter + 1});
    }
    return result;
}
