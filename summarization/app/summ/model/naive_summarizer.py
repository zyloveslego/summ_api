from app.summ.model.summarizer import Summarizer
import app.utils as Utils
import math
import random


class NaiveSummarizer(Summarizer):
    def __init__(self, language):
        self.utils = Utils.factory(language)

    def update_count(self, limitation_method, counter, sentence):
        if limitation_method == "sentence_ratio":
            return counter + 1
        if limitation_method == "words_count":
            return counter + self.utils.word_count(sentence)
        if limitation_method == "length_ratio":
            return counter + len(sentence)
        if limitation_method == "sentence_count":
            return counter + 1

    def get_limitation(self, limitation_method, sentence_list, para):
        if limitation_method == "sentence_ratio":
            return math.ceil(len(sentence_list) * para)
        if limitation_method == "words_count":
            return para
        if limitation_method == "length_ratio":
            return sum([len(x) for x in sentence_list]) * para
        if limitation_method == "sentence_count":
            return para

    def _get_limitation_method(self, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None):
        if length_ratio:
            return "length_ratio", length_ratio
        if sentence_ratio:
            return "sentence_ratio", sentence_ratio
        if words_count:
            return "words_count", words_count
        if sentence_count:
            return "sentence_count", sentence_count

    def summarize(self, text, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None, score=False):
        if not length_ratio and not sentence_ratio and not words_count and not sentence_count:
            print("please at choose a summary length")
            return None

        if isinstance(text, list):
            sentence_list = text
        else:
            sentence_list = self.utils.split_sentences(text)

        limitation_method, para = self._get_limitation_method(length_ratio, sentence_ratio, words_count, sentence_count)
        limitation = self.get_limitation(limitation_method, sentence_list, para)
        selected_sentence = []
        _counter = 0
        for sentence in sentence_list:
            selected_sentence.append(sentence)
            _counter = self.update_count(limitation_method, _counter, sentence)
            if _counter > limitation:
                break
        return selected_sentence

    def summarize_rand_sen(self, text, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None, score=False):
        if not length_ratio and not sentence_ratio and not words_count and not sentence_count:
            print("please at choose a summary length")
            return None

        if isinstance(text, list):
            sentence_list = text
        else:
            sentence_list = self.utils.split_sentences(text)
        limitation_method, para = self._get_limitation_method(length_ratio, sentence_ratio, words_count, sentence_count)
        limitation = self.get_limitation(limitation_method, sentence_list, para)
        selected_sentence = []
        _counter = 0
        sentence_index = random.sample(range(0, len(sentence_list) - 1), len(sentence_list) - 1)
        selected_sentence_index = []
        for index in sentence_index:
            selected_sentence_index.append(index)
            _counter = self.update_count(limitation_method, _counter, sentence_list[index])
            if _counter > limitation:
                break
        selected_sentence_index.sort()
        for index in selected_sentence_index:
            selected_sentence.append(sentence_list[index])
        return selected_sentence
