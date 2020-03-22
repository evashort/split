import re

tokenRegex = re.compile(r'\w+|[^ ]')

def tokenize(text):
    return (
        (match.start(), sanitize(match[0])) \
            for match in tokenRegex.finditer(text)
    )

def sanitize(token):
    translations = {
        '\n': '↵',
        '\t': '→'
    }
    token = token.lower()
    return translations.get(token, token)

if __name__ == '__main__':
    print(list(tokenize('a,~  1bA\n  \tC')))
    #a#,#~#1ba#\n#\t#C#
