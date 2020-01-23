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
    # https://www.researchgate.net/publication/43789438_A_Fast_Algorithm_for_Finding_the_non_Dominated_Set_in_Multiobjective_Optimization
    testData = [
        (0.94, 2934, 5.3, 289),
        (0.35, 3599, 6.6, 45),
        (0.76, 2780, 5.4, 23),
        (0.88, 1998, 8, 598),
        (0.39, 3476, 8.7, 444),
        (0.86, 3331, 7.9, 99),
        (0.27, 2597, 9.1, 188),
        (0.91, 2318, 2.1, 239),
        (0.73, 3273, 4.9, 177),
        (0.53, 4055, 7.7, 328)
    ]
    # negate because paper maximizes but our code minimizes
    testData = [tuple(-x for x in v) for v in testData]
    vectorNames = {vector: f'P{i + 1}' for i, vector in enumerate(testData)}
    result = nonDominatedSet(testData)
    print([vectorNames[vector] for vector in result])
