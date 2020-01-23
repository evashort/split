def nonDominatedSet(solutions):
    # https://www.researchgate.net/publication/43789438_A_Fast_Algorithm_for_Finding_the_non_Dominated_Set_in_Multiobjective_Optimization
    solutions.sort()
    result = []
    for new in solutions:
        if any(dominates(old, new) for old in result):
            continue

        result[:] = [old for old in result if not dominates(new, old)]
        result.append(new)

    return result

def dominates(a, b):
    '''return true if a dominates b or a == b'''
    return all(xa <= xb for xa, xb in zip(a, b))

if __name__ == '__main__':
    import random
    random.seed('reproducible test data 1')
    for i in range(1000):
        testData = [
            tuple(random.random() for j in range(50)) \
                for i in range(20)
        ]
        naiveNDS = {
            vector for vector in testData if not any(
                dominates(other, vector) \
                    for other in testData \
                        if other != vector
            )
        }
        nds = set(nonDominatedSet(testData))
        assert nds == naiveNDS
