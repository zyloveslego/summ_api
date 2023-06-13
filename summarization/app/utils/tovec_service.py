from gensim.models import KeyedVectors
import requests
import summarization.app.definitions as definitions
from itertools import combinations as _combinations
import json


class ToVecService:
    # a class instance holder
    _instance = {}

    # new singleton method
    def __new__(cls, language, w2v_model, w2v_web_api_url):
        """
        this maintain a singleton instance
        :param language: chinese of english
        :param w2v_model: a w2v model
        :param w2v_web_api_url: a w2v api
        :return:
        """
        if language not in cls._instance:
            cls._instance[language] = super(ToVecService, cls).__new__(cls)
        return cls._instance[language]

    def __init__(self, language, w2v_model, w2v_web_api_url):
        self.language = language
        self._w2v_model = w2v_model
        self._w2v_web_api_url = w2v_web_api_url

    @classmethod
    def set_model(cls, language, model_path):
        """
        set the model by model path, this also check the instance holder
        :param language: chinese or english
        :param model_path: a model path, usually define in definition.py
        :return:
        """
        if language in cls._instance:
            print("Your init request for ToVecService has been denied because an exist instance.")
            return cls._instance[language]

        print("--------Loading Mode--------")
        model = KeyedVectors.load_word2vec_format(model_path)
        print("--------Success--------")
        return cls(language, model, None)

    @classmethod
    def set_web_api(cls,language, url, port, path):
        """
        set the model by web api, this also check the instance holder
        set the a web api model, this for test only, since request need lots of time.
        :param language: chinese or english
        :param url: api url
        :param port:
        :param path:
        :return:
        """
        if language in cls._instance:
            return cls._instance[language]

        port = str(port)
        if "/" in path or not path:
            web_api_url = url + ":" + port + path
        else:
            web_api_url = url + ":" + port + path
        return cls(language, None, web_api_url)

    @classmethod
    def set_default_by_language(cls, language):
        """
        set the model by info in the definition.py
        :param language: chinese
        :return:
        """
        if language == "english":
            if definitions.W2V_MODE == "API":
                return ToVecService.set_web_api(language, url=definitions.W2V_API_WEB_API_URL,
                                                port=definitions.W2V_API_WEB_API_PORT,
                                                path=definitions.W2V_API_WEB_API_PATH)
            else:
                return ToVecService.set_model(language, model_path=definitions.W2V_EN_MODEL_PATH)
        else:
            if definitions.W2V_MODE == "API":
                return ToVecService.set_web_api(language, url=definitions.W2V_API_WEB_API_URL,
                                                port=definitions.W2V_API_WEB_API_PORT,
                                                path=definitions.W2V_API_WEB_API_PATH)
            else:
                return ToVecService.set_model(language, model_path=definitions.W2V_CN_MODEL_PATH)

    def word_similarity(self, w1, w2):
        """
        :param w1: word 1
        :param w2: word 2
        :return: w2v similarity
        """
        try:
            if self._w2v_web_api_url:
                return float(self._request_word_similarity(w1, w2))
            return self._model_word_similarity(w1, w2)
        except KeyError:
            return 0

    def pairwise_word_similarity(self, word_list):
        try:
            if self._w2v_web_api_url:
                return self._request_pairwise_word_similarity(word_list)
            pair_similarity = dict()
            for w1, w2 in _combinations(word_list, 2):
                pair_similarity[(w1, w2)] = self._model_word_similarity(w1, w2)
            return pair_similarity
        except KeyError:
            return 0

    def wmd(self, s1, s2):
        """
        :param s1: doc 1
        :param s2: doc 2
        :return: document similarity
        """
        if self._w2v_web_api_url:
            return float(self._request_wmd(s1, s2))
        return self._w2v_model.wmdistance(s1, s2)

    def pairwise_wmd(self, sentence_list):
        try:
            if self._w2v_web_api_url:
                return self._request_pairwise_wmd(sentence_list)
            pair_similarity = dict()
            for s1, s2 in _combinations(sentence_list, 2):
                pair_similarity[(s1, s2)] = self._w2v_model.wmdistance(s1, s2)
            return pair_similarity
        except KeyError:
            return 0

    def sentence_similarity(self, s1, s2):
        pass

    def _model_word_similarity(self, w1, w2):
        return self._w2v_model.similarity(w1, w2)

    def _request_word_similarity(self, w1, w2):
        request_url = "http://" + self._w2v_web_api_url + "/similarity?"
        request_url += "w1=" + w1 + "&" + "w2=" + w2
        r = requests.get(request_url)

        if "Internal Server Error" in r.text:
            return 0
        else:
            return r.text.replace("\n", "").replace("\"", "").replace("'","")

    def _request_pairwise_word_similarity(self, word_list):
        request_url = "http://" + self._w2v_web_api_url + "/pairwise_word_similarity"
        r = requests.post(request_url, data={"word_list": "#".join(word_list)})

        pair_similarity = dict()
        if "Internal Server Error" in r.text:
            return pair_similarity
        else:
            temp = json.loads(r.text)
            for key, val in temp.items():
                pair_similarity[tuple(key.split('#'))] = float(val)
            return pair_similarity

    def _request_pairwise_wmd(self, sentence_list):
        request_url = "http://" + self._w2v_web_api_url + "/pairwise_wmd"

        # check if separator already in sentence
        if sum([1 for sen in sentence_list if "#" in sen]) != 0:
            return dict()
        r = requests.post(request_url, data={"sentence_list": "#".join(sentence_list)})

        pair_similarity = dict()
        if "Internal Server Error" in r.text:
            return pair_similarity
        else:
            temp = json.loads(r.text)
            for key, val in temp.items():
                pair_similarity[tuple(key.split('#'))] = float(val)
            return pair_similarity

    def _model_wmd(self, s1, s2):
        return self._w2v_model.wmdistance(s1, s2)

    def _request_wmd(self, s1, s2):
        # if use fasttext model, no check needed
        # w1 = check(s1)
        # w2 = check(s2)
        request_url = "http://" + self._w2v_web_api_url + "/wmd?"
        request_url += "s1=" + s1 + "&" + "s2=" + s2
        r = requests.get(request_url)
        if "Internal Server Error" in r.text:
            return 0
        else:
            print(r.text)
            return r.text.replace("\n", "").replace("\"", "").replace("'","")

    def _check(self, word):
        if "-" in word:
            phrase = ' '.join(str(e) for e in word.split("-"))
            return phrase
        else:
            return word
