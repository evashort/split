#ifndef BESTREPEATEDPATHS_H
#define BESTREPEATEDPATHS_H

#include <string>
#include <vector>

#include "repeatedPaths.h"

template<class T>
struct RepeatedPath {
    std::vector<T> path;
    std::vector<int> positions;
};

struct PathScore {
    int pathLength;
    int partialLength;
};

bool operator>(const PathScore& lhs, const PathScore& rhs);
bool operator>=(const PathScore& lhs, const PathScore& rhs);

template<class T>
class BestRepeatedPathGenerator {
private:
    std::vector<T> sequence;
    RepeatedPathGenerator<T> generator;
    std::vector<std::vector<T> > stagedPaths;
    int stagedCycleCount;
    PathScore stagedScore;
public:
    BestRepeatedPathGenerator(std::vector<T> sequence, int minCycleCount=2);
    bool hasNext();
    std::vector<RepeatedPath<T> > next(int ticks);
};

template<class T>
std::map<T, std::vector<int> > getTokenPositions(
    const std::vector<T> &sequence,
    int minCycleCount
);

template<class T>
bool hasSubcycle(const std::vector<T> &path);

template<class T>
std::vector<int> getPathPositions(
    const std::vector<T> &path,
    const std::vector<T> &sequence
);

template<class T>
int getPartialLength(
    const std::vector<T> &path,
    const std::vector<T> &sequence,
    int lastStop
);

#endif
