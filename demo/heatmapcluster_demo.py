# Copyright (c) 2015, Warren Weckesser.  All rights reserved.
# This software is licensed according to the "BSD 2-clause" license.

import numpy as np
import matplotlib.pyplot as plt
from heatmapcluster import heatmapcluster


def make_data(size, seed=None):
    if seed is not None:
        np.random.seed(seed)

    s0 = np.random.gamma(7, 6, size=size[1])
    s1 = np.random.gamma(6, 8, size=size[1])
    s2 = np.random.gamma(5, 6, size=size[1])
    s = np.vstack((s0, s1, s2))
    i = np.random.choice(range(len(s)), size=size[0])
    x = s[i]

    t0 = np.random.gamma(8, 3, size=size[0])
    t1 = np.random.gamma(5, 3.0, size=size[0])
    t2 = np.random.gamma(6, 2.1, size=size[0])
    t = np.vstack((t0, t1, t2))
    j = np.random.choice(range(len(t)), size=size[1])

    x += 1.1*t[j].T

    x += 2*np.random.randn(*size)

    row_labels = [('R%02d' % k) for k in range(x.shape[0])]
    col_labels = [('C%02d' % k) for k in range(x.shape[1])]

    return x, row_labels, col_labels


x, row_labels, col_labels = make_data(size=(64, 48), seed=12345)

h = heatmapcluster(x, row_labels, col_labels,
                   num_row_clusters=3, num_col_clusters=0,
                   label_fontsize=6,
                   xlabel_rotation=-75,
                   cmap=plt.cm.coolwarm,
                   show_colorbar=True,
                   top_dendrogram=True)
plt.show()
