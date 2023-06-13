from summarization.app.summ.model.summarizer import Summarizer
from summarization.app.keywords.keyword import KeyWord, INVERTED_PYRAMID, PYRAMID, HOURGLASS, UNIFORM
import summarization.app.utils as Utils
import operator
import math
import nltk
from summarization.app.topic_modeling.clustering.spectral_clustering import SpectralClustering
from summarization.app.keywords.keysentence import KeySentence


def softplus_enhancement(keywords_tuples):
    index = 0
    for keyword, score in keywords_tuples:
        enhanced_score = math.log(1 + math.exp(score))
        keywords_tuples[index] = keyword, enhanced_score
        index = index + 1


class KWSummarizer(Summarizer):
    def __init__(self, language):
        self.utils = Utils.factory(language)

    # TODO TW_STV TW_WMD
    @staticmethod
    def factory(language, summarizer_name, customized_textrank=None):
        """
        TW: short for textrank_word, use only Textrank result, add up word score for a sentence score.
        TW_T: short for textrank_texttiling, add texttiling for sentence selecting, for a better diverse.
        TW_STV: short for textrank_word_STV, instead of texttiling for summary diverse.
                add a STV sentence embedding to count sentence similarity.
        TW_WMD: short for textrank_word_WMD, similar as TW_STV, compute the sentence similarity by using WMD.
        TWSC: add spectual clustering for topic modeling
        :param language:
        :param summarizer_name:
        :param customized_textrank:
        :return:
        """
        customized_textrank = KeyWord.basic_init(language=language) if not customized_textrank else customized_textrank
        # parser_name = ap means this parse all the articles doc name starts with AP
        if summarizer_name == "TW":
            return TextrankWord(language, customized_textrank, keyword_enhance=False)
        if summarizer_name == "E_TW":
            return TextrankWord(language, customized_textrank)
        if summarizer_name == "TW_T":
            return TWTexttiling(language, customized_textrank, keyword_enhance=False)
        if summarizer_name == "E_TW_T":
            return TWTexttiling(language, customized_textrank)
        if summarizer_name == "CTW":
            return CombinedTexRankWord(language, customized_textrank, keyword_enhance=False)
        if summarizer_name == "TWSC":
            return TWSC(language, customized_textrank, keyword_enhance=False)
        else:
            # Parser for other format hasn't been writen yet
            assert 0, "bad weighting method request: " + summarizer_name

    def format_result_by_para(self, text, summary):
        para = self.utils.split_para(text)

        # set the belong
        for index in range(0, len(summary) - 1):
            for p_no, p in enumerate(para):
                if summary[index] in p and summary[index + 1] not in p:
                    summary[index] = summary[index] + "\n"
                    break
        return summary

    def summarize(self, text, article_structure=INVERTED_PYRAMID, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None, show_score=False, show_ranking=False):
        raise NotImplementedError

    def _keywords_extract(self, text):
        raise NotImplementedError

    def _keywords_enhancement(self, keywords_tuples):
        raise NotImplementedError

    def _sentence_scoring(self, keywords, sentences):
        raise NotImplementedError

    def _sentence_reordering(self, selected_sentence, sentences, show_score, show_ranking):
        raise NotImplementedError

    def _get_best_sentence(self, scored_sentence_dict):
        raise NotImplementedError

    def _get_limitation_method(self, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None):
        if length_ratio:
            return "length_ratio", length_ratio
        if sentence_ratio:
            return "sentence_ratio", sentence_ratio
        if words_count:
            return "words_count", words_count
        if sentence_count:
            return "sentence_count", sentence_count

    def _sentence_selecting(self, limitation_method, sentence_list, scored_sentence_dict, para):
        def update_count(limitation_method, counter, sentence):
            if limitation_method == "sentence_ratio":
                return counter + 1
            if limitation_method == "words_count":
                return counter + self.utils.word_count(sentence)
            if limitation_method == "length_ratio":
                return counter + len(sentence)
            if limitation_method == "sentence_count":
                return counter + 1

        def get_limitation(limitation_method, sentence_list, scored_sentence_dict, para):
            if limitation_method == "sentence_ratio":
                return math.ceil(len(scored_sentence_dict) * para)
            if limitation_method == "words_count":
                return para
            if limitation_method == "length_ratio":
                return sum([len(x) for x in sentence_list]) * para
            if limitation_method == "sentence_count":
                return para

        limitation = get_limitation(limitation_method, sentence_list, scored_sentence_dict, para)
        selected_sentence = {}

        # general cases
        _counter = 0
        ranking = 1
        while _counter < limitation:
            # find the sentence with highest score, then append and removle the sentence.
            if len(scored_sentence_dict) == 0:
                break
            sentence = self._get_best_sentence(scored_sentence_dict)
            selected_sentence[sentence] = (scored_sentence_dict[sentence], ranking)
            ranking += 1
            del scored_sentence_dict[sentence]
            _counter = update_count(limitation_method, _counter, sentence)

        # restrict word count
        # _counter = 0
        # for sentence, value in scored_sentence_dict.items():
        #     words_in_sentence = update_count(limitation_method, _counter, sentence) - _counter
        #
        #     if abs(limitation - _counter - words_in_sentence) > abs(limitation - _counter):
        #         return selected_sentence
        #
        #     selected_sentence.append(sentence)
        #     _counter += words_in_sentence

        return selected_sentence


# TODO words not working
class TextrankWord(KWSummarizer):
    def __init__(self, language, customized_textrank, keyword_enhance=True):
        super().__init__(language)
        self.textrank = customized_textrank
        self._keyword_enhance = keyword_enhance

    def summarize(self, text, article_structure=INVERTED_PYRAMID, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None, show_score=False, show_ranking=False):
        """
        :param text: can be a sentence list or a text, note that better to use a sentence list,
                        since the split sentence function is not perform very good
        :param length_ratio: the length ratio, should be between 0 - 1, count the character length.
        :param sentence_ratio: the sentence no ratio. should be between 0 - 1, count the ratio of the sentence no
        :param words_count: number of word count
        :param sentence_count: number f sentence count
        :param score: set to true to get a sentence: score dict otherwise get a sentence list
        :return: a list of sentence
        """
        if not length_ratio and not sentence_ratio and not words_count and not sentence_count:
            print("please at least choose a summary length")
            return None
        # Step 0: Set sentence_list if not exist
        if isinstance(text, list):
            sentence_list = text
        else:
            sentence_list = self.utils.split_sentences(text)

        # Step 1: Use keywords extractor get keywords with score.
        keywords = self._keywords_extract(" ".join(sentence_list), article_structure=article_structure)

        # Step 2: Enhance the score by using some enhancement method like softplus
        if self._keyword_enhance:
            self._keywords_enhancement(keywords)

        # Step 3: Scoring the sentence by combine the keywords.
        scored_sentence_dict = self._sentence_scoring(keywords, sentence_list)

        # Step 4: select sentence
        limitation_method, para = self._get_limitation_method(length_ratio, sentence_ratio, words_count, sentence_count)
        selected_sentence = self._sentence_selecting(limitation_method, sentence_list, scored_sentence_dict, para)

        # Step 5: put the sentence back to its original order
        return self._sentence_reordering(selected_sentence, sentence_list, show_score, show_ranking)

    def _keywords_extract(self, text, article_structure=INVERTED_PYRAMID):
        """
        Step one: Use keywords extractor get keywords with score.
        :return: a tuple list each tuple contains a keyword and a score [(keyword, score), (keyword, score)]
        """
        if article_structure == UNIFORM:
            return self.textrank.extract(text, ratio=1, position_topic_biased=0, return_scores=True)
        else:
            return self.textrank.extract(text, ratio=1, position_topic_biased=1,
                                     article_structure=article_structure, return_scores=True)

    def _keywords_enhancement(self, keywords_tuples):
        """
        Step two: Enhance the score by using some enhancement method like softplus
        :param keywords_tuples:
        :return:
        """
        return softplus_enhancement(keywords_tuples)

    def _sentence_scoring(self, keywords, sentences):
        """
        Step three: Scoring the sentence by combine the keywords.
                    Let the keywords be None if scoring the sentence directly.
        :param keywords:
        :param sentences:
        :return:
        """
        scored_sentence_dict = {}
        for index, sentence in enumerate(sentences):
            _score = 0
            token_list = self.utils.tokenize(sentence)
            for keyword, score in keywords:
                if keyword in token_list:
                    # # word_count could be how many time that the keyword appear in a sentence.
                    word_count = sentence.count(keyword)
                    # # word_count could be 1 if we only see if the keyword exist
                    # word_count = 1
                    _score = _score + score * word_count
            scored_sentence_dict[sentence] = _score
        return scored_sentence_dict

    def _sentence_reordering(self, selected_sentence, sentences, show_score, show_ranking):
        """
        :param selected_sentence: {sentence:(score, ranking)}
        :param sentences:
        :param show_score:
        :param show_ranking:
        :return:
        """
        summary = []
        for i, sentence in enumerate(sentences):
            if sentence in selected_sentence:
                if show_ranking and show_score:
                    summary.append((i, sentence, *selected_sentence[sentence]))
                elif show_score:
                    summary.append((i, sentence, selected_sentence[sentence][0]))
                elif show_ranking:
                    summary.append((i, sentence, selected_sentence[sentence][1]))
                else:
                    summary.append(sentence)
        return summary

    def _get_best_sentence(self, scored_sentence_dict):
        return max(scored_sentence_dict.items(), key=operator.itemgetter(1))[0]


class TWSC(TextrankWord):
    def __init__(self, language, customized_textrank, keyword_enhance=True):
        super().__init__(language, customized_textrank, keyword_enhance=keyword_enhance)
        self.sc = SpectralClustering(language)

    def _get_cluster_no(self, sentences):
        # maximum 8  minimum 1
        return max(min(math.floor(0.3 * len(sentences)), 8), 1)

    def _sort_sentences_by_clusters(self, scored_sentence_dict):
        sentences = list(scored_sentence_dict.keys())
        # get the sentence dict
        cluster_no = self._get_cluster_no(sentences)
        sen_with_cluster = self.sc.clustering(sentences, cluster_no)

        # list index is the cluster, each item in the list is a ordered sentence dict.
        cluster_lst = []
        for i in range(cluster_no):
            cluster_lst.append(dict())

        # add sentence to the each dict
        for sentence in sen_with_cluster:
            _cluster = sen_with_cluster[sentence]
            score = scored_sentence_dict[sentence]

            _dct = cluster_lst[_cluster]
            _dct[sentence] = score

        # get a sorted sentence list
        sorted_sen = []
        while len(sorted_sen) != len(scored_sentence_dict):
            _dct = {}
            # in round robin fashion, sort the sentence with the highest score from each cluster.
            for cluster in cluster_lst:
                if len(cluster) == 0:
                    continue
                sentence = self._get_best_sentence(cluster)
                score = cluster[sentence]
                del cluster[sentence]
                _dct[sentence] = score

            sorted_sen.extend(sorted(_dct, key=_dct.get, reverse=True))
        return sorted_sen

    def _sentence_selecting(self, limitation_method, text, scored_sentence_dict, para):
        def update_count(limitation_method, counter, sentence):
            if limitation_method == "sentence_ratio":
                return counter + 1
            if limitation_method == "words_count":
                return counter + self.utils.word_count(sentence)
            if limitation_method == "length_ratio":
                return counter + len(sentence)
            if limitation_method == "sentence_count":
                return counter + 1

        def get_limitation(limitation_method, text, scored_sentence_dict, para):
            if limitation_method == "sentence_ratio":
                return math.ceil(len(scored_sentence_dict) * para)
            if limitation_method == "words_count":
                return para
            if limitation_method == "length_ratio":
                return len(text) * para
            if limitation_method == "sentence_count":
                return para

        limitation = get_limitation(limitation_method, text, scored_sentence_dict, para)
        selected_sentence = {}
        sorted_sentences = self._sort_sentences_by_clusters(scored_sentence_dict)

        # general cases
        _counter = 0
        for sentence in sorted_sentences:
            selected_sentence[sentence] = scored_sentence_dict[sentence]
            _counter = update_count(limitation_method, _counter, sentence)
            if _counter >= limitation:
                break

        return selected_sentence


class TWTexttiling(TextrankWord):
    def __init__(self, language, customized_textrank, keyword_enhance=True):
        super().__init__(language, customized_textrank, keyword_enhance=keyword_enhance)

    # TODO finish this sentence selecting method
    def _get_best_sentence(self, scored_sentence_dict):
        pass

    def _texttiling(self, text):
        """
        :param text:
        :return: a sentence dict key is the sentence, and the value is the para number.
        """
        # must replace \n first other wise, it will return an error.
        text = text.replace('\n', '\n\n')
        paragraphs = nltk.tokenize.texttiling.TextTilingTokenizer().tokenize(text)

        texttiled_sentence_dict = {}
        for para_num, para in enumerate(paragraphs):
            if len(para) == 0:
                continue
            sentences = self.utils.split_sentences(para)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 0:
                    texttiled_sentence_dict[sentence] = para_num
        return texttiled_sentence_dict


class CombinedTexRankWord(TextrankWord):
    def __init__(self, language, customized_textrank, keyword_enhance=True):
        super().__init__(language, customized_textrank, keyword_enhance)
        self.key_sentence_extract = KeySentence.basic_init(language)

    def summarize(self, text, article_structure=INVERTED_PYRAMID, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None, show_score=False, show_ranking=False):
        if not length_ratio and not sentence_ratio and not words_count and not sentence_count:
            print("please at least choose a summary length")
            return None
        # Step 0: Set sentence_list if not exist
        if isinstance(text, list):
            sentence_list = text
        else:
            sentence_list = self.utils.split_sentences(text)

        # Step 1: Use keywords extractor get keywords with score.
        keywords = self._keywords_extract(" ".join(sentence_list), article_structure=article_structure)

        # Step 2: Enhance the score by using some enhancement method like softplus
        if self._keyword_enhance:
            self._keywords_enhancement(keywords)

        # Step 3: Scoring the sentence by combine the keywords.
        scored_sentence_dict = self._sentence_scoring(keywords, sentence_list)

        # this is a sentence rank provide by textrank
        # sentence_rank_by_textrank = SentenceRank(sentence_list, language="english")
        sentence_rank_list = self.key_sentence_extract.extract(text, ratio=1, return_scores=True, position_topic_biased=1, article_structure=article_structure)

        self.combine_score(scored_sentence_dict, sentence_rank_list)

        # Step 4: select sentence
        limitation_method, para = self._get_limitation_method(length_ratio, sentence_ratio, words_count, sentence_count)
        selected_sentence = self._sentence_selecting(limitation_method, sentence_list, scored_sentence_dict, para)

        return self._sentence_reordering(selected_sentence, sentence_list, show_score, show_ranking)

    def combine_score(self, SWD_sentence_dict, sentence_rank_list):
        def normalize(score, max_score, scale=10):
            return score/max_score*scale

        total_SWD_score  = sum(SWD_sentence_dict.values())
        sentence_rank_list.sort(key=lambda s: s[1], reverse=True)
        total_sentence_score = sum(score for sen, score in sentence_rank_list)

        for sentence, score in sentence_rank_list:
            text = sentence
            tr_score = normalize(score, total_sentence_score)
            if text.strip() not in SWD_sentence_dict:
                print("find not match sentence！！！！！！！！！！！！！！！！！！！！")
            else:
                SWD_score = normalize(SWD_sentence_dict[text], total_SWD_score)
                SWD_sentence_dict[text] = tr_score + SWD_score
