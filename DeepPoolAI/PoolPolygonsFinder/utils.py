import math

def join_ways(ways):
    """
    OSM ofter returns polygons as list of unsorted ways. This method joins those ways, that in returned list
    each ways is one polygon.

    Parameters
    ----------
    ways : list
        List of ways (list) of (lat, long) tuples. 

    Returns
    -------
    List of cyclic ways. Each represent one polygon.
    """

    if len(ways) == 0:
        return []
    ways = ways.copy()
    out_ways = []
    while len(ways) > 1:
        new_ways = []
        for w in ways:
            last = len(w) - 1
            if w[0][0] == w[last][0] and w[0][1] == w[last][1]:
                out_ways.append(w)
            else:
                new_ways.append(w)
        ways = new_ways
        if len(ways) <= 1:
            continue
        min_dist = (math.inf, None, None, None)
        for w1 in range(len(ways)):
            for w2 in range(w1 + 1, len(ways)):
                for comb in range(4):
                    edge1 = 0 if (comb % 2) else len(ways[w1]) - 1
                    edge2 = 0 if (comb < 2) else len(ways[w2]) - 1
                    p1 = ways[w1][edge1]
                    p2 = ways[w2][edge2]
                    dist = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
                    if dist < min_dist[0]:
                        min_dist = (dist, w1, w2, comb)
        way1 = ways[min_dist[1]].copy()
        way2 = ways[min_dist[2]].copy()
        if min_dist[3] % 2:
            way1.reverse()
        if min_dist[3] >= 2:
            way2.reverse()
        ways.pop(min_dist[2])
        ways.pop(min_dist[1])
        ways.append(way1 + way2)
    if len(ways) == 1:
        out_ways.append(ways[0])
    return out_ways
