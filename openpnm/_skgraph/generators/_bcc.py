import scipy.spatial as sptl
import scipy.sparse as sprs
from openpnm._skgraph.generators import cubic
import numpy as np


def bcc(shape, spacing=1, mode='kdtree'):
    r"""
    Generate a body-centered cubic lattice

    Parameters
    ----------
    shape : array_like
        The number of unit cells in each direction.  A unit cell has vertices
        on all 8 corners and a single pore at its center.
    spacing : array_like or float
        The size of a unit cell in each direction. If an scalar is given it is
        applied in all 3 directions.
    mode : str
        Dictate how neighbors are found.  Options are:
            ===============  =====================================================
            mode             meaning
            ===============  =====================================================
            'kdtree'         Uses ``scipy.spatial.KDTree`` to find all neighbors
                             within the unit cell.
            'triangulation'  Uses ``scipy.spatial.Delaunay`` to find all neighbors.
            ===============  =====================================================
    Returns
    -------
    network : dict
        A dictionary containing 'vert.coords' and 'edge.conns'

    Notes
    -----
    It is not clear whether KDTree of Delaunay are faster. In fact it is
    surely possible to find the neighbors formulaically but this is not
    implemented yet.

    """
    from openpnm.topotools import tri_to_am
    shape = np.array(shape)
    spacing = np.array(spacing)
    net1 = cubic(shape=shape+1, spacing=1)
    net2 = cubic(shape=shape, spacing=1)
    net2['coords'] += 0.5
    crds = np.concatenate((net1['coords'], net2['coords']))
    if mode.startswith('tri'):
        tri = sptl.Delaunay(points=crds)
        am = tri_to_am(tri)
        conns = np.vstack((am.row, am.col)).T
        # Trim diagonal connections between cubic pores
        L = np.sqrt(np.sum(np.diff(crds[conns], axis=1)**2, axis=2)).flatten()
        conns = conns[L <= 1]
    elif mode.startswith('kd'):
        tree1 = sptl.KDTree(crds)
        # Method 1
        hits = tree1.query_ball_point(crds, r=1)
        # Method 2: Not sure which is faster
        # tree2 = sptl.KDTree(crds)
        # hits = tree1.query_ball_tree(tree1, r=1)
        indices = np.hstack(hits)
        # Convert to CSR matrix
        indptr = [len(i) for i in hits]
        indptr.insert(0, 0)
        indptr = np.cumsum(indptr)
        am = sprs.csr_matrix((np.ones_like(indices), indices, indptr))
        am = sprs.triu(am, k=1)
        am = am.tocoo()
        conns = np.vstack((am.row, am.col)).T

    d = {}
    d['coords'] = crds*spacing
    d['conns'] = conns
    return d


if __name__ == '__main__':
    import openpnm as op
    import matplotlib.pyplot as plt
    pn = op.network.GenericNetwork()
    net = bcc([3, 3, 3], 1, mode='tri')
    net['pore.coords'] = net.pop('coords')
    net['throat.conns'] = net.pop('conns')
    pn.update(net)
    pn['pore.all'] = np.ones((np.shape(pn.coords)[0]), dtype=bool)
    pn['throat.all'] = np.ones((np.shape(pn.conns)[0]), dtype=bool)
    fig, ax = plt.subplots()
    op.topotools.plot_connections(pn, ax=ax)
    op.topotools.plot_coordinates(pn, ax=ax)
