import unittest
import os
from gensim.corpora.dictionary import Dictionary
from app.utils.utils_EN import UtilsEN
from gensim.models.ldamodel import LdaModel
from app.definitions import BBC_DIR


def read_file(pre_path, file):
    with open(os.path.join(pre_path, file), mode='r') as f:
        text = f.read()
        text = text.replace("\n\n", " ")
        text = text.replace("\n", " ")
        return text


class TestDUCFetcher(unittest.TestCase):

    def setUp(self):
        # self.sc = SpectralClustering("english")
        # self.customized_textrank = KeyWord.basic_init(language="english", weighting_method="CO_OCCUR")
        self._load_data()
        self.util = UtilsEN("english")
        pass

    def _load_data(self):
        self.news = {}
        pre_path = os.path.join(BBC_DIR, 'testing')
        for _cluster in os.listdir(pre_path):
            if "DS_Store" in _cluster:
                continue

            _c_path = os.path.join(pre_path, _cluster)
            self.news[_cluster] = []
            for file_name in os.listdir(_c_path):
                if "DS_Store" in file_name:
                    continue
                text = read_file(_c_path, file_name)
                self.news[_cluster].append(text)

    def test_clustering_wmd_negative(self):
        data = []
        for ele in self.news:
            data.extend(self.news[ele])

        res = self.sc.clustering(data, 5)

        for ele in res:
            print(ele[0:100], res[ele])

    def test_keyword_indexing_wmd(self):
        data = []
        for ele in self.news:
            for text in self.news[ele]:
                key = self.customized_textrank.extract(text, ratio=1, scores=True, position_biased=False,
                                                       combination=True, textrank_original=False)
                if len(key) > 30:
                    key = key[:30]
                kw = " ".join([ele[0] for ele in key])
                data.append(kw)

        res = self.sc.clustering(data, 5)

        for ele in res:
            print(ele, res[ele])

    def test_clustering_lda(self):
        cor = []
        pre_path = os.path.join(BBC_DIR, 'corpus')
        for _cluster in os.listdir(pre_path):
            if "DS_Store" in _cluster:
                continue
            _c_path = os.path.join(pre_path, _cluster)
            for file_name in os.listdir(_c_path):
                if "DS_Store" in file_name:
                    continue
                text = read_file(_c_path, file_name)
                tokens = self.util.tokenize(text)
                filtered_tokens = self.util.tokens_filter(tokens)
                filtered_tokens = [t for t in filtered_tokens if t != ""]
                cor.append(filtered_tokens)
        dictionary = Dictionary(cor)
        common_corpus = [dictionary.doc2bow(text) for text in cor]
        lda = LdaModel(common_corpus, num_topics=5, alpha='auto', id2word=dictionary)
        topics = lda.print_topics()

        for topic in topics:
            print(topic)

        for cls in self.news:
            for text in self.news[cls]:
                tokens = self.util.tokenize(text)
                filtered_tokens = self.util.tokens_filter(tokens)
                filtered_tokens = [t for t in filtered_tokens if t != ""]
                unseen = dictionary.doc2bow(filtered_tokens)
                vector = lda[unseen]
                print(vector)


if __name__ == '__main__':
    unittest.main()
