# Copyright (c) 2017, Warren Weckesser.  All rights reserved.
# This software is licensed according to the "BSD 2-clause" license.

from __future__ import division as _division

import numpy as _np
from scipy import __version__ as _scipy__version__
from scipy.spatial import distance as _distance
import scipy.cluster.hierarchy as _hierarchy
import matplotlib.pyplot as _plt
from mpl_toolkits import axes_grid1 as _axes_grid1


__version__ = "0.1.2"

_scipy_version = tuple(int(v) for v in _scipy__version__.split('.')[:2])


class HeatmapClusterResults(object):
    """
    Instances of this class are returned by the function heatmapcluster().
    """

    def __init__(self, **kwds):
        for name, value in kwds.items():
            setattr(self, name, value)


def heatmapcluster(x, row_labels, col_labels,
                   num_row_clusters=None, num_col_clusters=None,
                   label_fontsize=8, cmap=None, show_colorbar=True,
                   colorbar_pad=0.5,
                   top_dendrogram=True,
                   xlabel_rotation=-45,
                   ylabel_rotation=0,
                   figsize=(12, 8)):
    """
    Use matplotlib to generate a heatmap with row and column dendrograms.

    Parameters
    ----------
    x : 2D numpy array with shape (m, n)
        The array holds m "observations", where each observation is of n
        variables or features.
    row_labels : list of strings
        The labels of the rows of x.
    col_labels : list of strings
        The labels of the columns of x.
    num_row_clusters : int
        Number of clusters to be given separate colors in the row
        dendrogram (i.e. the dendrogram on the left).
    num_col_clusters : int
        Number of clusters to be given separate colors in the column
        dendrogram (i.e. the dendrogram on the top).
    label_fontsize : int (or value compatible with matplotlib font sizes)
        Font size of the labels along the axes of the heatmap.
    cmap : matplotlilb color map
        The color map to use in the heatmap.
    show_colorbar : bool
        If True (the default), show a colorbar for the heatmap on the right.
    colorbar_pad: float
        Float to determine padding of colorbar. Useful if Y axis labels are
        long.
    top_dendrogram : bool
        If True (the default), compute a column dendrogram and display it
        on top of the heatmap.  (A row dendrogram is always computed and
        shown on the right of the heatmap.)
    xlabel_rotation : int
        Rotation angle (in degrees) of the labels along the x axis of
        the heatmap.
    ylabel_rotation : int
        Rotation angle (in degrees) of the labels along the y axis of
        the heatmap.
    figsize : tuple of int
        Matplotlib figure size.

    Return value
    ------------
    results : Instance of HeatmapClusterResults
        An object with an assortment of attributes, some related to the
        dendrogram calculations, and some matplotlib objects used in the
        plot.

    """
    lnk0 = _hierarchy.linkage(_distance.pdist(x))
    if top_dendrogram:
        lnk1 = _hierarchy.linkage(_distance.pdist(x.T))
    else:
        lnk1 = None

    if cmap is None:
        cmap = _plt.rcParams['image.cmap']

    fig, ax_heatmap = _plt.subplots(figsize=figsize)
    ax_heatmap.yaxis.tick_right()

    # Create new axes on the left and on the top of the current axes.
    # These will hold the dendrograms.
    divider = _axes_grid1.make_axes_locatable(ax_heatmap)
    ax_dendleft = divider.append_axes("left", 1.2, pad=0.0,
                                      sharey=ax_heatmap)
    if top_dendrogram:
        ax_dendtop = divider.append_axes("top", 1.2, pad=0.0,
                                         sharex=ax_heatmap)
    else:
        ax_dendtop = None
    if show_colorbar:
        # Add an axis on the right for the colorbar.
        ax_colorbar = divider.append_axes("right", 0.2, pad=colorbar_pad)
    else:
        ax_colorbar = None

    ax_dendleft.set_frame_on(False)
    if top_dendrogram:
        ax_dendtop.set_frame_on(False)

    if num_row_clusters is None or num_row_clusters <= 1:
        left_threshold = -1
    else:
        left_threshold = 0.5*(lnk0[1-num_row_clusters, 2] +
                              lnk0[-num_row_clusters, 2])
    if _scipy_version < (0, 17):
        # Work around bug in older scipy, where the orientation was backwards.
        side_orientation = 'right'
    else:
        side_orientation = 'left'
    dg0 = _hierarchy.dendrogram(lnk0, ax=ax_dendleft,
                                orientation=side_orientation,
                                color_threshold=left_threshold,
                                no_labels=True)

    if top_dendrogram:
        if num_col_clusters is None or num_col_clusters <= 1:
            top_threshold = -1
        else:
            top_threshold = 0.5*(lnk1[1-num_col_clusters, 2] +
                                 lnk1[-num_col_clusters, 2])
        dg1 = _hierarchy.dendrogram(lnk1, ax=ax_dendtop,
                                    color_threshold=top_threshold,
                                    no_labels=True)
    else:
        dg1 = None

    # Reorder the values in x to match the order of the leaves of
    # the dendrograms.
    z = x[dg0['leaves'], :]
    if top_dendrogram:
        z = z[:, dg1['leaves']]
        ymax = ax_dendtop.get_xlim()[1]
    else:
        ymax = 1
    im = ax_heatmap.imshow(z[::-1], aspect='auto', cmap=cmap,
                           interpolation='nearest',
                           extent=(0, ymax, 0, ax_dendleft.get_ylim()[1]))

    xlim = ax_heatmap.get_xlim()[1]
    ncols = len(col_labels)
    halfxw = 0.5*xlim/ncols

    ax_heatmap.xaxis.set_ticks(_np.linspace(halfxw, xlim - halfxw, ncols))
    if top_dendrogram:
        ax_heatmap.xaxis.set_ticklabels(_np.array(col_labels)[dg1['leaves']])
    else:
        ax_heatmap.xaxis.set_ticklabels(col_labels)

    ylim = ax_heatmap.get_ylim()[1]
    nrows = len(row_labels)
    halfyw = 0.5*ylim/nrows

    ax_heatmap.yaxis.set_ticks(_np.linspace(halfyw, ylim - halfyw, nrows))
    ax_heatmap.yaxis.set_ticklabels(_np.array(row_labels)[dg0['leaves']])

    # Make the dendrogram labels invisible.
    _plt.setp(ax_dendleft.get_yticklabels() + ax_dendleft.get_xticklabels(),
              visible=False)
    if top_dendrogram:
        _plt.setp(ax_dendtop.get_xticklabels() + ax_dendtop.get_yticklabels(),
                  visible=False)

    # Hide all tick lines.
    lines = (ax_heatmap.xaxis.get_ticklines() +
             ax_heatmap.yaxis.get_ticklines() +
             ax_dendleft.xaxis.get_ticklines() +
             ax_dendleft.yaxis.get_ticklines())
    _plt.setp(lines, visible=False)
    if top_dendrogram:
        lines = (ax_dendtop.xaxis.get_ticklines() +
                 ax_dendtop.yaxis.get_ticklines())
        _plt.setp(lines, visible=False)

    xlbls = ax_heatmap.xaxis.get_ticklabels()
    _plt.setp(xlbls, rotation=xlabel_rotation)
    _plt.setp(xlbls, fontsize=label_fontsize)

    ylbls = ax_heatmap.yaxis.get_ticklabels()
    _plt.setp(ylbls, rotation=ylabel_rotation)
    _plt.setp(ylbls, fontsize=label_fontsize)

    if show_colorbar:
        cb = _plt.colorbar(im, cax=ax_colorbar)
    else:
        cb = None

    results = HeatmapClusterResults(
        row_linkage=lnk0,
        row_dendrogram=dg0,
        col_linkage=lnk1,
        col_dendrogram=dg1,
        fig=fig,
        heatmap_image=im,
        heatmap_axis=ax_heatmap,
        colorbar=cb,
        colorbar_axis=ax_colorbar,
        left_dendrogram_axis=ax_dendleft,
        top_dendrogram_axis=ax_dendtop,
    )

    return results
