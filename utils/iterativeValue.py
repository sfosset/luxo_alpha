"""This file is an implementation of the Value Iteration algorithm for a 6*10
cliff problem.


|   |   |   |   |   |   |   |   |   |   |
|---|---|---|---|---|---|---|---|---|---|
|   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |
| A | * | * | * | * | * | * | * | * | B |

The program should learn how to go from A to B. The * squares represents a
cliff. The dict V has an entry for each square, represented by his coordinates
(i,j) where i is the line, j the column and A is (0,0).

V[(i,j)] is the value state, modified with each iteration following the
equation in the nextV method.
P[(i,j)] is the corresponding policy. It associates a state to the state with
the highest state value among his four neighbours.

"""

def nextV(V):
    """Computes the next V iteration from the previous one."""
    nextV = {}
    P = p(V)

    for state in V:
        nextV[state] = r(P[state])+0.9*V[P[state]]

    return nextV


def p(V):
    """Generates the policy p corresponding to V.

    Args:
        V (dict): the state value vector, for example :
            {(0,0): 8,
             (1,0): 9,
             (2,0): 3.2}

    Returns:
        dict: a dictionnary that directly associates a state to a state without
        using any action. For example :

        {(0,0): (1,0),
         (1,0): (1,1),
         (2,0): (2,1)}

    """
    P={}
    for state in V:
        bestValue = -10000;
        if (state[0]-1, state[1]) in V and V[(state[0]-1, state[1])]>bestValue:
            bestValue = V[(state[0]-1, state[1])]
            P[state]=(state[0]-1, state[1])
        if (state[0]+1, state[1]) in V and V[(state[0]+1, state[1])]>bestValue:
            bestValue = V[(state[0]+1, state[1])]
            P[state] = (state[0]+1, state[1])
        if (state[0], state[1]-1) in V and V[(state[0], state[1]-1)]>bestValue:
            bestValue = V[(state[0], state[1]-1)]
            P[state] = (state[0], state[1]-1)
        if (state[0], state[1]+1) in V and V[(state[0], state[1]+1)]>bestValue:
            bestValue = V[(state[0], state[1]+1)]
            P[state] = (state[0], state[1]+1)

    return P


def r(state):
    """Computes the reward for a given state.

    Args:
        state (tuple): a square (i,j)
    Returns:
        int: a reward following this rules :

            * Give 10 points if the state is the finish state
            * Give -1000 points if the state is in the cliff

    """
    if state == (0,10):
        return 10
    elif state[0]==0 and state != (0,0):
        return -1000
    else:
        return 0


def test(firstState, P):
    """Generates a path following a given policy starting at a given state

    Args:
        firstState (tuple) : the starting square (i,j)
        P (dict) : a policy. For example :
            {(0,0): (1,0),
             (1,0): (1,1),
             (2,0): (2,1)}
    """
    print(str(firstState))
    nextState = P[firstState]
    print(str(nextState))
    for i in range(20):
        nextState = P[nextState]
        print(str(nextState))


if __name__=="__main__":

    firstV = {}
    for i in range(0,7):
        for j in range (0,11):
            firstV[(i,j)]=10

    V=firstV
    for t in range(100):
        V=nextV(V)

    P = p(V)

    for state in V:
        print('{} : {},{}'.format(state, V[state], P[state]) )

    test((5,1), P)
