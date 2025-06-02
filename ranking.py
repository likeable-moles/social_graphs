import random as r


def compute_agony(G, ranking):
    # print("ranking: {}".format(ranking))
    agony = 0
    for u, v in G.edges():
        # Given a rank function r, we say that an edge e = (u,v) ∈ E is forward if
        # r(u) < r(v). Similarly, we say that e = (u,v) ∈ E is backward if r(u) ≥ r(v). (Nikolaj Tatti)
        # u -> v
        # if r[u] >= r[v] then the edge direction is against the ranking.
        ru = ranking[u]
        rv = ranking[v]
        agony += max(0, ru - rv + 1)
    return agony


def min_agony_ranking(G):
    nodes = list(G.nodes())
    nodes.reverse()
    min_agony = float('inf')
    best_ranking = None

    # Randomly choose from possible rankings and minimize graph agony.
    for i in range(1_000_000):
        ranking = {node: r.choice(nodes) for node in nodes}
        agony = compute_agony(G, ranking)
        if agony < min_agony:
            min_agony = agony
            best_ranking = ranking
            print("agony: {}".format(agony))
            if agony == 0:
                break

    return best_ranking, min_agony

