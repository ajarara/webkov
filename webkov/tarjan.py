

class Visited():
    def __init__(self, index, lowlink, onstack, neighbors):
        self.index = index
        self.lowlink = lowlink
        self.onstack = onstack
        self.neighbors = neighbors


def tarjan(adj_list):
    '''
    Input is an adjacency list, like this one:
    {
        1: [2, 3, 4, 5],
        2: [1, 3, 5],
        3: [1],
        4: [],
        5: [1, 2, 3, 4, 5],
    }
    yielding: [{1, 2, 3, 5}, {4}] or any permutation.
    '''

    # we're going to be mutating this.
    al = adj_list.copy()
    # we wrap index in a list so that we can mutate the reference
    # within the scope of strongconnect.
    # a little hacky.
    idx = [0]
    # if I understand this correctly, the reason we keep track of
    # onstack is so that we can check if a vertex is on the stack in
    # constant time.
    stack = []
    out = []

    def strongconnect(v, neighbors):
        assert type(neighbors) == list
        al[v] = Visited(index=idx[0], lowlink=idx[0],
                        onstack=True, neighbors=neighbors)
        idx[0] += 1
        stack.append(v)

        # since we still have the reference to neighbors, why not just use it?
        for child in neighbors:
            if type(al[child]) == list:
                # we haven't visited this yet.
                strongconnect(child, al[child])
                al[v].lowlink = min(al[v].lowlink, al[child].lowlink)
            elif al[child].onstack:
                al[v].lowlink = min(al[v].lowlink, al[child].index)

        if al[v].lowlink == al[v].index:
            # regurgitate our stack
            scc = set()
            # would it be clearer to set 'first', then set it to false
            # in the loop possibly repeatedly?
            w = stack.pop()
            al[w].onstack = False
            scc.add(w)
            while w != v:
                w = stack.pop()
                al[w].onstack = False
                scc.add(w)
            out.append(scc)

    for vertex, adj in al.items():
        if type(adj) == list:
            strongconnect(vertex, adj)

    return out
