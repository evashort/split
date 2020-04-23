#include "preprocessor.h"

using namespace std;

vector<string> tokenize(string text) {
    vector<string> result;
    regex tokenRegex(R"(\w+|[^ ])");
    sregex_iterator matchIter(text.begin(), text.end(), tokenRegex);
    sregex_iterator matchEnd;
    for (; matchIter != matchEnd; matchIter++) {
        result.push_back(sanitize(matchIter->str()));
    }
    return result;
}

string sanitize(string token) {
    if (token == "\n") {
        return "↵";
    }
    if (token == "\t") {
        return "→";
    }
    string result = token;
    for (int i = 0; i < token.size(); i++) {
        result[i] = tolower(token[i]);
    }
    return result;
}
