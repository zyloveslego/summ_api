import unittest
from app.topic_modeling.clustering.spectral_clustering import SpectralClustering

# s1 = "Why does Ebola keep coming back?"
# s2 = "Ebola is back – and WHO is preparing for worst-case scenario"
# s3 = "health workers threaten strike amid Ebola back"
# s4 = "Ebola Returns Just as the White House Loses Its Top Biodefense Expert"
#
# s15 = "Trade War Or Not, Threatened Soybean Tariffs Having An Impact"
# s16 = "Why a Trade War Shouldn't Wreck World Markets"
# s17 = "America Will Win the Trade War with China"
# s18 = "US envoy: trade war with Beijing won't happen"



s1 = "He had recently been appointed CFO of Swedish Match, a producer of smokeless tobacco, cigars, matches, and lighters."
s2 = "Red Man, Swedish Match’s chewing tobacco brand, was sold only in the United States and was the market leader, with a 43% market share in 2004, and Swedish Match was hoping for further growth of snus products."
s3 = "In the Swedish market more and more people felt there were advantages to snus, a more socially accepted tobacco product, and Swedish Match was uniquely positioned to take advantage of this growth."
s4 = "Kreuger had become wealthy by building Swedish Match into an international business empire comprised of national monopolies in safety matches."
s5 = "Six of these merged to form Jönköping och Vulcans Tändsticksfabriks AB (J&V), controlling 80% of the Swedish match market and threatening the Kreuger family company."
s6 = "In addition to snus, snuff, chewing tobacco, and cigars, Swedish Match also produced pipe tobacco, although this was a declining market."
s7 = "By 1992, this match business was combined with the largest Swedish tobacco company, under the Swedish Match name."
s8 = "At the time of his death, Swedish Match had a globally dominant position, selling 66% of the world’s matches."
s9 = "After smokeless tobacco, Swedish Match’s most important single product was cigars, which comprised 24% of sales and 59% of operating income in 2004."
s10 = "By 2005, Swedish Match was a worldwide leader in smokeless tobacco products including snuff, snus, and chewing tobacco."
s11 = "At that time, the business consisted of matches and lighters, cigarettes, and niche tobacco products (cigars, pipe tobacco, and smokeless tobacco)."
s12 = "As a first step, in 1917, Swedish Match acquired majority holdings in Denmark’s three match companies, but this tested Kreuger’s ability to borrow in Sweden to the limit."
s13 = "traditional solvency ratios such as equity over total assets poorly reflect these risks.” Instead, he felt that a policy that targeted a rating such as BBB+, a reasonable interest coverage ratio, and suitable market leverage would provide a better target for the firm."
s14 = "Costs matched revenues fairly well, so the net currency exposure of Swedish Match was low."
s15 = "Though the board did not know it yet, Dahlgren was considering a radical proposal: a substantial increase in the firm’s leverage, implemented with a Euro-denominated bond issue, and combined with an aggressive program of share repurchases."


sentences = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15]


class TestDUCFetcher(unittest.TestCase):

    def setUp(self):
        self.sc = SpectralClustering("english")

    def test_clustering_wmd_negative(self):
        res = self.sc.clustering(sentences, 3)
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
