import numpy as np
from scipy.linalg import orthogonal_procrustes

from app.preprocessing.WordVectors import WordVectors
from .global_align import GlobalAlignConfig

# Noise-Aware alignment of word embeddings
# Source: https://github.com/NoaKel/Noise-Aware-Alignment
class NoiseAwareAlignConfig:
    def __init__(self, name="unnamed", is_soft=True):
        self._name = name
        self._is_soft = is_soft

    def align(self, wv1, wv2):
        """
        aligns wv1 to wv2 using noise-aware alignment
        """
        Q, alpha, t_indices, f_indices = noise_aware(
            wv1.vectors, wv2.vectors, self._is_soft
        )
        _wv1v = np.matmul(wv1.vectors, Q)
        _wv1 = WordVectors(wv1.get_words(), _wv1v)
        return _wv1, wv2, Q


def P(Y, dim, mu, s):
    """
    calculates gaussian probability
    :param Y: matrix
    :param dim: dimention
    :param mu: mu - mean
    :param s: sigma - variance
    :return: probability
    """
    C = -dim / 2 * (np.log(2 * np.pi * s))
    exp = -0.5 * np.einsum(
        "ij, ij -> i", Y - mu, np.dot(np.eye(dim) * (1 / s), (Y - mu).T).T
    )
    return C + exp


def EM_aux(X, Y, alpha, Q, sigma, muy, sigmay, is_soft):
    """
    EM noise aware
    :param X: matrix 1
    :param Y: matrix 2
    :param alpha: percentage of clean pairs
    :param Q: transform matrix
    :param sigma: clean pairs variance
    :param muy: noisy pairs mean
    :param sigmay: noisy pair variance
    :param is_soft: true - soft EM, false - hard EM
    :return: transform matrix, alpha, clean indices, noisy indices
    """
    n, dim = X.shape
    threshold = 0.01
    prev_alpha = -1
    j = -1
    while abs(alpha - prev_alpha) > threshold:
        j = j + 1
        prev_alpha = alpha
        # E-step
        ws = [0] * n
        nom = [0] * n
        sup = [0] * n
        nom[:] = np.log(alpha) + P(Y, dim, np.dot(X, Q), sigma)
        sup[:] = np.log((1 - alpha)) + P(Y, dim, muy, sigmay)
        m = max(nom)
        ws[:] = np.exp(nom[:] - m) / (np.exp(nom[:] - m) + np.exp(sup[:] - m))
        ws = np.where(np.isnan(ws), 0, ws)
        # M-step
        if is_soft:
            sum_ws = float(sum(ws))
            alpha = sum_ws / float(n)
            Q, _ = orthogonal_procrustes(
                np.multiply(np.array(ws).reshape((n, 1)), X),
                np.multiply(np.array(ws).reshape((n, 1)), Y),
            )
            sigma = sum(
                np.linalg.norm(np.dot(X[i, :], Q) - Y[i, :]) ** 2 * ws[i]
                for i in range(0, n)
            ) / (sum_ws * dim)
            muy = sum(Y[i, :] * (1 - ws[i]) for i in range(0, n)) / (n - sum_ws)
            sigmay = sum(
                np.linalg.norm(muy - Y[i, :]) ** 2 * (1 - ws[i]) for i in range(0, n)
            ) / ((n - sum_ws) * dim)
        else:  # hard EM
            t_indices = np.where(np.asarray(ws) >= 0.5)[0]
            f_indices = np.where(np.asarray(ws) < 0.5)[0]
            assert len(t_indices) > 0
            assert len(f_indices) > 0
            X_clean = np.squeeze(X[[t_indices], :])
            Y_clean = np.squeeze(Y[[t_indices], :])
            alpha = float(len(t_indices)) / float(n)
            Q, _ = orthogonal_procrustes(X_clean, Y_clean)
            sigma = sum(
                np.linalg.norm(np.dot(X[i, :], Q) - Y[i, :]) ** 2 for i in t_indices
            ) / (len(t_indices) * dim)
            muy = sum(Y[i, :] for i in f_indices) / len(f_indices)
            sigmay = sum(np.linalg.norm(muy - Y[i, :]) ** 2 for i in f_indices) / (
                len(f_indices) * dim
            )

        # print('iter:', j, 'alpha:', round(alpha,3), 'sigma:', round(sigma,3), 'sigmay', round(sigmay,3))

    t_indices = np.where(np.asarray(ws) >= 0.5)[0]
    f_indices = np.where(np.asarray(ws) < 0.5)[0]
    return np.asarray(Q), alpha, t_indices, f_indices


def noise_aware(X, Y, is_soft=False):
    """
    noise aware alignment
    :param X: matrix 1
    :param Y: matrix 2
    :param is_soft: true - soft EM, false - hard EM
    :return: transform matrix, alpha, clean indices, noisy indices
    """
    n, dim = X.shape
    Q_start, _ = orthogonal_procrustes(X, Y)
    sigma_start = np.linalg.norm(np.dot(X, Q_start) - Y) ** 2 / (n * dim)
    muy_start = np.mean(Y, axis=0)
    sigmay_start = np.var(Y)
    alpha_start = 0.5
    return EM_aux(
        X, Y, alpha_start, Q_start, sigma_start, muy_start, sigmay_start, is_soft
    )
