#ifndef REPEATEDPATHS_H
#define REPEATEDPATHS_H

#include <queue>
#include <map>
#include <vector>

struct Range {
    int start;
    int stop;
};

bool operator<(const Range& lhs, const Range& rhs);

struct Key {
    int cycleCount;
    std::vector<Range> shape;
};

bool operator<(const Key& lhs, const Key& rhs);

template<class T>
struct PathInfo {
    int cycleCount;
    std::vector<Range> shape;
    std::vector<T> path;
};

template<class T>
class RepeatedPathGenerator {
private:
    std::map<T, std::vector<int> > tokenPositions;
    int minCycleCount;
    std::map<
        std::vector<Range>,
        std::vector<std::vector<T> >
    > shapePaths;
    std::priority_queue<Key> fringe;
    Key key;
    std::vector<std::vector<T> > paths;
    // apparently the compiler can't figure out that this is a typename
    // unless we tell it
    typename std::vector<std::vector<T> >::const_iterator pathIter;
public:
    RepeatedPathGenerator(
        std::map<T, std::vector<int> > tokenPositions,
        int sequenceLength,
        int minCycleCount=2
    );
    PathInfo<T> next();
};

int countNonOverlapping(const std::vector<Range> &ranges);

std::vector<Range> addTail(
    const std::vector<Range> &ranges,
    const std::vector<int> &positions
);

#endif
