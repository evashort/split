#ifndef PREPROCESSOR_H
#define PREPROCESSOR_H

#include <cctype>
#include <regex>
#include <string>
#include <vector>

std::vector<std::string> tokenize(std::string text);

std::string sanitize(std::string token);

#endif
