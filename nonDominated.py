def nonDominated(solutions, key=None, uniq=False, existing=[]):
    # https://www.researchgate.net/publication/43789438_A_Fast_Algorithm_for_Finding_the_non_Dominated_Set_in_Multiobjective_Optimization
    solutions.sort(reverse=True, key=key)
    result = existing
    for new in solutions:
        if any(
            dominates(old, new, key=key, uniq=uniq) \
                for old in result
        ):
            continue

        result = [
            old for old in result \
                if not dominates(new, old, key=key, uniq=uniq)
        ]
        result.append(new)

    return result

def dominates(a, b, key=None, uniq=False):
    '''
    return true if a dominates b
    if uniq=True, also return true if a == b
    '''
    if key is not None:
        a, b = key(a), key(b)

    return all(xa >= xb for xa, xb in zip(a, b)) \
        and (
            uniq or any(xa > xb for xa, xb in zip(a, b))
        )

if __name__ == '__main__':
    import random
    random.seed('reproducible test data 1')
    for i in range(1000):
        testData = [
            tuple(random.random() for j in range(4)) \
                for i in range(200)
        ]
        naiveNDS = {
            vector for vector in testData if not any(
                dominates(other, vector) \
                    for other in testData \
                        if other != vector
            )
        }
        partialNDS = nonDominated(testData[:100], uniq=True)
        nds = set(
            nonDominated(testData[100:], uniq=True, existing=partialNDS)
        )
        assert nds == naiveNDS
