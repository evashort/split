#include <iostream>
#include "preprocessor.h"
#include "bestRepeatedPaths.h"

using namespace std;

int main(int argc, char **argv) {
    string text = R"({
  "colors": [
    {
      "color": "black",
      "category": "hue",
      "type": "primary",
      "code": {
        "rgba": [255,255,255,1],
        "hex": "#000"
      }
    },
    {
      "color": "white",
      "category": "value",
      "code": {
        "rgba": [0,0,0,1],
        "hex": "#FFF"
      }
    },
    {
      "color": "red",
      "category": "hue",
      "type": "primary",
      "code": {
        "rgba": [255,0,0,1],
        "hex": "#FF0"
      }
    },
    {
      "color": "blue",
      "category": "hue",
      "type": "primary",
      "code": {
        "rgba": [0,0,255,1],
        "hex": "#00F"
      }
    },
    {
      "color": "yellow",
      "category": "hue",
      "type": "primary",
      "code": {
        "rgba": [255,255,0,1],
        "hex": "#FF0"
      }
    },
    {
      "color": "green",
      "category": "hue",
      "type": "secondary",
      "code": {
        "rgba": [0,255,0,1],
        "hex": "#0F0"
      }
    },
  ]
}
)";
    vector<string> tokens = tokenize(text);
    cout << "input: ";
    vector<string>::const_iterator tokenIter = tokens.cbegin();
    for (; tokenIter != tokens.cend(); tokenIter++) {
        cout << *tokenIter;
    }
    cout << endl;
    BestRepeatedPathGenerator<string> generator(
        vector<string>(tokens.cbegin(), tokens.cend())
    );
    while (generator.hasNext()) {
        vector<RepeatedPath<string> > repeatedPaths = generator.next(1000);
        vector<RepeatedPath<string> >::const_iterator repeatedPathIter
            = repeatedPaths.cbegin();
        for (; repeatedPathIter != repeatedPaths.cend(); repeatedPathIter++) {
            vector<string> path = repeatedPathIter->path;
            vector<string>::const_iterator pathIter = path.cbegin();
            for (; pathIter != path.cend(); pathIter++) {
                cout << *pathIter;
            }
            cout << endl;
        }
    }
}
