import preprocessor
import mlcs

if __name__ == '__main__':
    def hasSubcycle(sequence):
        for cycleLength in range(1, len(sequence) // 2 + 1):
            cycleCount, remainder = divmod(len(sequence), cycleLength)
            badSequence = sequence[:cycleLength] * cycleCount \
                + sequence[:remainder]
            if sequence == badSequence:
                return True

        return False

    with open('testcases/colors.json') as f:
        text = f.read()
    tokens = [
        token for i, token in preprocessor.tokenize(text)
    ]
    for pathLength, positions in mlcs.mlcs(tokens):
        cycleCount, partialLength = divmod(len(positions), pathLength)
        print(''.join(tokens[p] for p in positions[:pathLength]))
        sequences = [
            [
                tokens[positions[j] + 1 : positions[j + 1]] \
                    for j in range(i, len(positions) - 1, pathLength)
            ] \
                for i in range(pathLength)
        ]
        sequences = [
            sequence for sequence in sequences \
                if all(sequence) and not hasSubcycle(sequence)
        ]
        for sequence in sequences:
            strings = list(map(''.join, sequence))
            print(f'    {strings[0]}', *strings[1:], sep=' ')

        print()
    # time complexity: 110595198
    # space complexity: 487550
