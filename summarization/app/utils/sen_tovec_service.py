from summarization.app.web_api.bert_service.service.client import BertClient
from itertools import combinations
from scipy import spatial
import numpy as np


class SenToVecService:
    # a class instance holder
    _instance = {}

    # new singleton method
    def __new__(cls, language, bert_model):
        """
        this maintain a singleton instance
        :param language: chinese of english
        :param w2v_model: a w2v model
        :param w2v_web_api_url: a w2v api
        :return:
        """
        if language not in cls._instance:
            cls._instance[language] = super(SenToVecService, cls).__new__(cls)
        return cls._instance[language]

    def __init__(self, language, bert_model):
        self.language = language
        # self._bert_model = bert_model
        self.bert_model = bert_model

    # @classmethod
    # def set_model(cls, language, model_path):
    #     """
    #     set the model by model path, this also check the instance holder
    #     :param language: chinese or english
    #     :param model_path: a model path, usually define in definition.py
    #     :return:
    #     """
    #     if language in cls._instance:
    #         print("Your init request for ToVecService has been denied because an exist instance.")
    #         return cls._instance[language]
    #
    #     print("--------Loading Mode--------")
    #     model = KeyedVectors.load_word2vec_format(model_path)
    #     print("--------Success--------")
    #     return cls(language, model, None)
    #
    # @classmethod
    # def set_web_api(cls,language, url, port, path):
    #     """
    #     set the model by web api, this also check the instance holder
    #     set the a web api model, this for test only, since request need lots of time.
    #     :param language: chinese or english
    #     :param url: api url
    #     :param port:
    #     :param path:
    #     :return:
    #     """
    #     if language in cls._instance:
    #         return cls._instance[language]
    #
    #     port = str(port)
    #     if "/" in path or not path:
    #         web_api_url = url + ":" + port + path
    #     else:
    #         web_api_url = url + ":" + port + path
    #     return cls(language, None, web_api_url)
    #
    @classmethod
    def set_default_by_language(cls, language):
        """
        set the model by info in the definition.py
        :param language: chinese
        :return:
        """
        return cls(language, BertClient())

    def s2v(self, s):
        return self.bert_model.encode([s])[0]

    def sentence_simiarity(self, s1, s2, encoded=False):
        if not encoded:
            sentence_vectors = self.sentences_encode([s1, s2])
            s1 = sentence_vectors[0]
            s2 = sentence_vectors[1]
        return 1 - spatial.distance.cosine(s1, s2)

    def pairwise_sentence_similarity(self, sentence_list):
        encoded_sentences = self.sentences_encode(sentence_list)

        sen_arr = np.array([[i] for i in range(len(sentence_list))])

        similarity_matix = np.zeros((sen_arr.shape[0], sen_arr.shape[0]), dtype='float')
        iterator = combinations(range(sen_arr.shape[0]), 2)
        for i, j in iterator:
            similarity_matix[i, j] = self.sentence_simiarity(encoded_sentences[i], encoded_sentences[j], encoded=True)

        similarity_matix = similarity_matix + similarity_matix.T

        for i in range(len(sentence_list)):
            similarity_matix[i, i] = self.sentence_simiarity(encoded_sentences[i], encoded_sentences[i],  encoded=True)
        return similarity_matix

    def sentences_encode(self, sentence_list):
        return self.bert_model.encode(sentence_list)