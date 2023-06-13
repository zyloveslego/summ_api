from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from nltk.corpus import stopwords
from summarization.app.keywords.textrank.tokenizer import Tokenizer
from summarization.app.topic_modeling.bbc_dataset import BBCDataset
import pickle


class TFIDFKeywords:
    def __init__(self, cv_model_path=None, tf_idf_path=None):
        self.stop_words = list(set(stopwords.words('english')))
        self.max_df = 0.95
        self.min_df = 1
        if not cv_model_path or not tf_idf_path:
            news = BBCDataset().news
            corpus = [x for x, l in news]
            self.cv, self.tfidf_transformer = self.tf_idf_training(corpus)
        else:
            with open(cv_model_path, 'rb') as f:
                self.cv = pickle.load(f)

            with open(tf_idf_path, 'rb') as f:
                self.tfidf_transformer = pickle.load(f)

        self.feature_names = self.cv.get_feature_names()

    def tf_idf_training(self, corpus):
        """
        :param corpus:  a list of text, where each text is a token list
        :return:
        """
        corpus = [" ".join(x) for x in corpus]

        count_vectorizer = CountVectorizer(max_df=self.max_df, min_df=self.min_df, stop_words=self.stop_words)

        # form the TF matrix
        word_count_vector = count_vectorizer.fit_transform(corpus)

        tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
        tfidf_transformer.fit(word_count_vector)

        with open('cv.pkl', 'wb') as f:
            pickle.dump(count_vectorizer, f)

        with open('tfidf_transformer.pkl', 'wb') as f:
            pickle.dump(tfidf_transformer, f)

        return count_vectorizer, tfidf_transformer

    def _sort_coo(self, coo_matrix):
        tuples = zip(coo_matrix.col, coo_matrix.data)
        return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

    def _extract_topn_from_vector(self, feature_names, sorted_items, topn=None):
        """get the feature names and tf-idf score of top n items"""

        # use only topn items from vector
        if topn:
            sorted_items = sorted_items[:topn]

        score_vals = []
        feature_vals = []
        for idx, score in sorted_items:
            # keep track of feature name and its corresponding score
            score_vals.append(round(score, 3))
            feature_vals.append(feature_names[idx])

        # create a tuples of feature,score
        # results = zip(feature_vals,score_vals)
        results = {}
        for idx in range(len(feature_vals)):
            results[feature_vals[idx]] = score_vals[idx]

        return results

    def extract(self, text, words=None):
        """
        :param text:
        :return:
        """
        tf_idf_vector = self.tfidf_transformer.transform(self.cv.transform([text]))

        sorted_items = self._sort_coo(tf_idf_vector.tocoo())

        keywords = self._extract_topn_from_vector(self.feature_names, sorted_items, words)

        return keywords


if __name__ == "__main__":
    tokenizer = Tokenizer.factory("english")
    with open("/Users/hao/Code/Summarization/tests/keywords_test/test_data/mihalcea_tarau.txt") as f:
        _news = f.read().replace("\n", " ")
        tokens = tokenizer.tokenize_by_word(_news, apply_token_filters=True)
        text = [unit.token for unit in tokens]
        print(text)
    news = BBCDataset().news
    corpus = [x for x, l in news]
    tf_idf_kw = TFIDFKeywords()
    tf_idf_kw.extract(" ".join(text))
