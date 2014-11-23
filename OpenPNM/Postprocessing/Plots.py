import scipy as _sp
import matplotlib.pylab as _plt

def profiles(network,
             fig=None,
             values=None,
             bins=[10,10,10]):
    r'''
    Compute the profiles for the property of interest and plots it in all
    three dimensions

    Parameters
    ----------
    network : OpenPNM Network object

    values : array_like, optional
        The pore property values to be plotted as a profile

    bins : int or list of ints, optional
        The number of bins to divide the domain into for averaging.

    Notes
    -----
    Either propname or values can be sent, but not both

    '''
    if fig is None:
        fig = _plt.figure()
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    ax = [ax1,ax2,ax3]
    xlab = ['x coordinate','y_coordinate','z_coordinate']
    for n in [0,1,2]:
        n_min, n_max = [_sp.amin(network['pore.coords'][:,n]), _sp.amax(network['pore.coords'][:,n])]
        steps = _sp.linspace(n_min,n_max,bins[n]+1,endpoint=True)
        vals = _sp.zeros_like(steps)
        for i in range(0,len(steps)-1):
            temp = (network['pore.coords'][:,n] > steps[i])*(network['pore.coords'][:,n] <= steps[i+1])
            vals[i] = _sp.mean(values[temp])
        yaxis = vals[:-1]
        xaxis = (steps[:-1] + (steps[1]-steps[0])/2)/n_max
        ax[n].plot(xaxis,yaxis,'bo-')
        ax[n].set_xlabel(xlab[n])
        ax[n].set_ylabel('Slice Value')
    fig.show()

def porosity_profile(network,
                      fig=None, axis=2):

    r'''
    Compute the porosity profile in all three dimensions

    Parameters
    ----------
    network : OpenPNM Network object
    axis : integer type 0 for x-axis, 1 for y-axis, 2 for z-axis

    Notes
    -----
    the area of the porous medium at any position is calculated from the
    maximum pore coordinates in each direction

    '''
    if fig is None:
        fig = _plt.figure()
    L_x = _sp.amax(network['pore.coords'][:,0])
    L_y = _sp.amax(network['pore.coords'][:,1])
    L_z = _sp.amax(network['pore.coords'][:,2])
    if axis is 0:
        xlab = 'x-direction'
        area = L_y*L_z
    elif axis is 1:
        xlab = 'y-direction'
        area = L_x*L_z
    else:
        axis = 2
        xlab = 'z-direction'
        area = L_x*L_y
    n_max = _sp.amax(network['pore.coords'][:,axis])
    steps = _sp.linspace(0,n_max,100,endpoint=True)
    vals = _sp.zeros_like(steps)
    rp = ((21/88.0)*network['pore.volume'])**(1/3.0)
    upper = network['pore.coords'][:,axis] + rp
    lower = network['pore.coords'][:,axis] - rp
    for i in range(0,len(steps)):
        temp = (upper > steps[i])*(lower < steps[i])
        vals[i] = (sum((22/7.0)*(rp[temp]**2 - (network['pore.coords'][:,axis][temp]-steps[i])**2)) \
        + _sp.sum(network['throat.area'][temp]))/area
    yaxis = vals
    xaxis = steps/n_max
    _plt.plot(xaxis,yaxis,'bo-')
    _plt.xlabel(xlab)
    _plt.ylabel('Porosity')
    fig.show()

def distributions(net,
                  fig = None,
                  throat_diameter='throat.diameter',
                  pore_diameter='pore.diameter',
                 throat_length='throat.length',
                 exclude_boundaries=True,
                 geom_list=None):
    r"""
    Plot a montage of key network size distribution histograms

    Parameters
    ----------
    net : OpenPNM Network Object
    The network for which the graphs are desired

    """
    if fig is None:
        fig = _plt.figure()

    if geom_list is not None:
        include_pores = [False]*net.num_pores()
        include_throats = [False]*net.num_throats()
        for geom in geom_list:
            include_pores = include_pores | net["pore."+geom]
            include_throats = include_throats | net["throat."+geom]
    else:
        include_pores = net["pore.all"]
        include_throats = net["throat.all"]
    pores = net.pores()[include_pores]
    throats = net.throats()[include_throats]


    ax1 = fig.add_subplot(221)
    ax1.hist(net[pore_diameter][pores],25,facecolor='green')
    ax1.set_xlabel('Pore Diameter')
    ax1.set_ylabel('Frequency')

    ax2 = fig.add_subplot(222)
    x = net.num_neighbors(pores,flatten=False)
    ax2.hist(x,25,facecolor='yellow')
    ax2.set_xlabel('Coordination Number')
    ax2.set_ylabel('Frequency')

    ax3 = fig.add_subplot(223)
    ax3.hist(net[throat_diameter][throats],25,facecolor='blue')
    ax3.set_xlabel('Throat Diameter')
    ax3.set_ylabel('Frequency')

    ax4 = fig.add_subplot(224)
    ax4.hist(net[throat_length][throats],25,facecolor='red')
    ax4.set_xlabel('Throat Length')
    ax4.set_ylabel('Frequency')
    fig.show()

def drainage_curves(inv_alg,
                    fig=None,
                    Pc='inv_Pc',
                    sat='inv_sat',
                    seq='inv_seq',
                    timing=None):
    r"""
    Plot a montage of key saturation plots

    Parameters
    ----------
    inv_alg : OpenPNM Algorithm Object
    The invasion algorithm for which the graphs are desired

    timing : string
    if algorithm keeps track of simulated time, insert string here.

    Examples
    --------
    >>> import OpenPNM
    >>> pn = OpenPNM.Network.TestNet()
    >>> geo = OpenPNM.Geometry.TestGeometry(network=pn,pores=pn.pores(),throats=pn.throats())
    >>> phase1 = OpenPNM.Phases.TestPhase(network=pn)
    >>> phase2 = OpenPNM.Phases.TestPhase(network=pn)
    >>> phys1 = OpenPNM.Physics.TestPhysics(network=pn, phase=phase1,pores=pn.pores(),throats=pn.throats())
    >>> phys2 = OpenPNM.Physics.TestPhysics(network=pn, phase=phase2,pores=pn.pores(),throats=pn.throats())
    >>> IP = OpenPNM.Algorithms.InvasionPercolation(network=pn)
    >>> IP.run(invading_phase=phase1, defending_phase=phase2, inlets=pn.pores('top'), outlets=pn.pores('bottom'))
    IP algorithm at 0 % completion at 0.0 seconds
    IP algorithm at 20 % completion at 0.0 seconds
    IP algorithm at 40 % completion at 0.0 seconds
    IP algorithm at 60 % completion at 0.0 seconds
    IP algorithm at 100% completion at  0.0  seconds
    >>> OpenPNM.Postprocessing.Plots.drainage_curves(IP,timing='inv_time')
    """
    inv_throats = inv_alg.toindices(inv_alg['throat.'+seq]>0)
    sort_seq = _sp.argsort(inv_alg['throat.'+seq][inv_throats])
    inv_throats = inv_throats[sort_seq]

    if fig is None:
        fig = _plt.figure(num=1, figsize=(13, 10), dpi=80, facecolor='w', edgecolor='k')
    ax1 = fig.add_subplot(231)   #left
    ax2 = fig.add_subplot(232)   #middle
    ax3 = fig.add_subplot(233)   #right
    ax4 = fig.add_subplot(234)   #left
    ax5 = fig.add_subplot(235)   #middle
    ax6 = fig.add_subplot(236)   #right

    ax1.plot(inv_alg['throat.'+Pc][inv_throats],inv_alg['throat.'+sat][inv_throats])
    ax1.set_xlabel('Capillary Pressure (Pa)')
    ax1.set_ylabel('Saturation')
    ax1.set_ylim([0,1])
    ax1.set_xlim([0.99*min(inv_alg['throat.'+Pc][inv_throats]),1.01*max(inv_alg['throat.'+Pc][inv_throats])])

    ax2.plot(inv_alg['throat.'+seq][inv_throats],inv_alg['throat.'+sat][inv_throats])
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Saturation')
    ax2.set_ylim([0,1])
    ax2.set_xlim([0,1.01*max(inv_alg['throat.'+seq][inv_throats])])

    if timing==None:
        ax3.plot(0,0)
        ax3.set_xlabel('No Time Data Available')
    else:
        ax3.plot(inv_alg['throat.'+timing][inv_throats],inv_alg['throat.'+sat][inv_throats])
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Saturation')
        ax3.set_ylim([0,1])
        ax3.set_xlim([0,1.01*max(inv_alg['throat.'+timing][inv_throats])])

    ax4.plot(inv_alg['throat.'+sat][inv_throats],inv_alg['throat.'+Pc][inv_throats])
    ax4.set_ylabel('Capillary Pressure (Pa)')
    ax4.set_xlabel('Saturation')
    ax4.set_xlim([0,1])
    ax4.set_ylim([0.99*min(inv_alg['throat.'+Pc][inv_throats]),1.01*max(inv_alg['throat.'+Pc][inv_throats])])

    ax5.plot(inv_alg['throat.'+seq][inv_throats],inv_alg['throat.'+Pc][inv_throats])
    ax5.set_xlabel('Simulation Step')
    ax5.set_ylabel('Capillary Pressure (Pa)')
    ax5.set_ylim([0.99*min(inv_alg['throat.'+Pc][inv_throats]),1.01*max(inv_alg['throat.'+Pc][inv_throats])])
    ax5.set_xlim([0,1.01*max(inv_alg['throat.'+seq][inv_throats])])

    if timing==None:
        ax6.plot(0,0)
        ax6.set_xlabel('No Time Data Available')
    else:
        ax6.plot(inv_alg['throat.'+timing][inv_throats],inv_alg['throat.'+Pc][inv_throats])
        ax6.set_xlabel('Time (s)')
        ax6.set_ylabel('Capillary Pressure (Pa)')
        ax6.set_ylim([0.99*min(inv_alg['throat.'+Pc][inv_throats]),1.01*max(inv_alg['throat.'+Pc][inv_throats])])
        ax6.set_xlim([0,1.01*max(inv_alg['throat.'+timing][inv_throats])])

    fig.subplots_adjust(left=0.08, right=0.99, top=0.95, bottom=0.1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    ax5.grid(True)
    ax6.grid(True)
    fig.show()

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
