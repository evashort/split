#include <iostream>
#include "bestRepeatedPaths.h"

using namespace std;

int main(int argc, char **argv) {
    string text = "actagcta";
    cout << "input: " << text << endl;
    BestRepeatedPathGenerator<char> generator(
        vector<char>(text.cbegin(), text.cend())
    );
    while (generator.hasNext()) {
        vector<RepeatedPath<char> > repeatedPaths = generator.next(1000);
        vector<RepeatedPath<char> >::const_iterator repeatedPathIter
            = repeatedPaths.cbegin();
        for (; repeatedPathIter != repeatedPaths.cend(); repeatedPathIter++) {
            vector<char> path = repeatedPathIter->path;
            cout << string(path.cbegin(), path.cend()) << endl;
        }
    }
}
