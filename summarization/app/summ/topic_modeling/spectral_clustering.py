from app.utils.tovec_service import ToVecService
import numpy as np
from sklearn.cluster import spectral_clustering
import sklearn.metrics.pairwise as pairwise
from itertools import combinations


# distance or sim functions
def _wmd_metric(x, y, to_vec_service):
    return to_vec_service.wmd(x, y)


# distance to sim functions
def negative_transfer(distance_matrix):
    sim_matrix = -distance_matrix + distance_matrix.max() - 1
    sim_matrix += 1
    return sim_matrix


def guassian_kernel_transfer(distance_matrix):
    return pairwise.rbf_kernel(distance_matrix)


class SpectralClustering:
    def __init__(self, language):
        self.language = language
        self.to_vec_service = ToVecService.set_default_by_language(language)

    def clustering(self, sentences, n_clusters, metric="WMD", distance_to_sim=negative_transfer):
        """
        :param sentences: a sentence list
        :param n_clusters: number of clusters, set to none if want to use the default setting
        :param metric: "WMD" or other callable that measure the distance,
        :param distance_to_sim: callable to transfer from distance to similarity. None if metric is similarity
        :return: sentence: cluster dict
        """
        # create a numpy array that contains index
        sen_arr = np.array([[i] for i in range(len(sentences))])
        if metric == "WMD":
            distance_matrix = self._pairwise_dist(sen_arr, sentences)
        else:
            distance_matrix = pairwise.pairwise_distances(sen_arr, metric=metric, n_jobs=-1)

        if distance_to_sim is not None:
            sim_matrix = distance_to_sim(distance_matrix)
        else:
            sim_matrix = distance_matrix

        sc = spectral_clustering(n_clusters=n_clusters, affinity=sim_matrix)

        return dict(zip(sentences, sc))

    def _pairwise_dist(self, sen_arr, sentences):
        combinations(range(len(sentences)), 2)

        out = np.zeros((sen_arr.shape[0], sen_arr.shape[0]), dtype='float')
        iterator = combinations(range(sen_arr.shape[0]), 2)
        for i, j in iterator:
            out[i, j] = _wmd_metric(sentences[i], sentences[j], self.to_vec_service)

        # Make symmetric
        # NB: out += out.T will produce incorrect results
        out = out + out.T

        # Calculate diagonal
        # NB: nonzero diagonals are allowed for both metrics and kernels
        for i in range(len(sentences)):
            out[i, i] = _wmd_metric(sentences[i], sentences[i], self.to_vec_service)
        return out
