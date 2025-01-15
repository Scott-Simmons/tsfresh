import numpy as np
from scipy.spatial.distance import cdist
cimport numpy as np


def approximate_entropy(object x, int m, double r):
    x = np.asarray(x, dtype=np.float64)

    cdef int N = x.size
    cdef np.ndarray[np.double_t, ndim=2] x_re
    r *= np.std(x)

    if r < 0:
        raise ValueError("Parameter r must be positive.")
    if N <= m + 1:
        return 0

    def _phi(int m):
        x_re = np.lib.stride_tricks.sliding_window_view(x, m)

        C = np.sum(
            cdist(x_re, x_re, metric='chebyshev') <= r,
            axis=0
        ) / (N - m + 1)

        return np.sum(np.log(C)) / (N - m + 1.0)

    return float(np.abs(_phi(m) - _phi(m + 1)))
