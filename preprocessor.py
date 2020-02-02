import re

tokenRegex = re.compile(r'\w+|[^ ]')

def tokenize(text):
    return (
        (match.start(), match[0].lower()) \
            for match in tokenRegex.finditer(text)
    )

if __name__ == '__main__':
    print(list(tokenize('a,~  1bA  \tC')))
    #a#,#~#1ba#\t#C#
