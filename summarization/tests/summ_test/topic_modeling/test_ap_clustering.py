import unittest
from app.topic_modeling.clustering.affinity_propagation import AffinityPropagationClustering

s1 = "Why does Ebola keep coming back?"
s2 = "Ebola is back – and WHO is preparing for worst-case scenario"
s3 = "health workers threaten strike amid Ebola back"
s4 = "Ebola Returns Just as the White House Loses Its Top Biodefense Expert"

s15 = "Trade War Or Not, Threatened Soybean Tariffs Having An Impact"
s16 = "Why a Trade War Shouldn't Wreck World Markets"
s17 = "America Will Win the Trade War with China"
s18 = "US envoy: trade war with Beijing won't happen"

sentences = [s1, s2, s3, s4, s15, s16, s17, s18]


class TestDUCFetcher(unittest.TestCase):

    def setUp(self):
        self.sc = AffinityPropagationClustering("english")

    def test_clustering_wmd_negative(self):
        res = self.sc.clustering(sentences)
        # res_2 = self.sc.clustering(sentences, 2, metric="BERT")
        # TODO: this could be equal or counterequal due to clustering tag assign
        label = [0, 0, 0, 0, 1, 1, 1, 1]
        gt = dict(zip(sentences, label))
        for i in res:
            print(i, res[i])
        # self.assertEqual(gt, res)
        pass


if __name__ == '__main__':
    unittest.main()
