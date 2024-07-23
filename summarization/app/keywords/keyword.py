import summarization.app.keywords.textrank.graph.graph_builder as graph_builder
import summarization.app.keywords.textrank.weighting as Weighting
from summarization.app.keywords.textrank.graph.pagerank_weighted import INVERTED_PYRAMID, PYRAMID, HOURGLASS, UNIFORM
from summarization.app.keywords.textrank.graph.pagerank_weighted import get_page_rank_score, WITH_POSITION_BIAS, \
    WITH_TFIDF_POSITION_BIAS, WITH_TOPIC_POSITION_BIAS, WITHOUT_BIAS, my_get_page_rank_score, \
    get_page_rank_score_combine_sentence
from summarization.app.keywords.textrank.syntactic_unit import SyntacticUnit
from summarization.app.keywords.textrank.tokenizer import Tokenizer
from summarization.app.utils import utils_EN, utils_CN
# from memory_profiler import profile


def _lemmas_to_words(token_dict):
    """
    from the word original to the word word, no effect on chinese. cause it have no word original
    :param token_dict:
    :return:
    """
    lemma_to_word = {}
    # unit is the syntactic unit
    for word, unit in token_dict.items():
        # token is the word original(stemmed words) ex. reconstruction -> construct
        # word is the original word: reconstruction
        lemma = unit.token
        if lemma in lemma_to_word:
            lemma_to_word[lemma].append(word)
        else:
            lemma_to_word[lemma] = [word]
    return lemma_to_word


class KeyWord(object):
    def __init__(self, language, tokenizer, weighting):
        """
        :param language: english or chines
        :param tokenizer:
        :param weighting:
        :param combinator:
        """
        self.language = language
        self.tokenizer = tokenizer
        self.weighting = weighting

    @classmethod
    def basic_init(cls, language, weighting_method="CO_OCCUR"):
        """
        :param language: english or chines
        :param candidate_generation_method: WORD means use only words, PHRASE is not available here
        :param weighting_method: See Weighing package for detail.
        """
        tokenizer = Tokenizer.factory(language)
        weighting = Weighting.factory(language, weighting_method, word_or_sentence="WORD")
        return cls(language, tokenizer, weighting)

    def _generate_candidate(self, text):
        """
        Accept text use the tokenizer to generate three tokenized text.
        :param text:
        :return: token_dict, tag_filtered_tokens, original_tokens
        token_list: is a syntactic unit list
        token_dict: is a syntactic unit dictionary, just removed the dupication
        original_tokens = is a list of words. not syntactic unit
        """
        # two syntatic units list, with out filters will return all the tokens, while the token list only contains token that pass certain filters.
        token_list, token_without_filter = self.tokenizer.tokenize_by_word(text, apply_token_filters=True,
                                                                           with_out_filter=True)
        # token list -> token dict {token.text, syntatic unit}
        token_dict = SyntacticUnit.to_dict(token_list)

        # apply pos tag filters
        # token list -> remove some by filters => tag filtered tokens
        tag_filtered_tokens = self.tokenizer.pos_tag_filter(token_list)

        # token_with_out_filter -> original_tokens, contains all the tokens
        original_tokens = SyntacticUnit.to_text_list(token_without_filter)

        # token_list = self.tokenizer.tokenize_by_sentence(text, apply_token_filters=True)
        # print(token_list)

        # import time
        # start0 = time.time()
        from nltk.tokenize import sent_tokenize
        # 我的返回结构
        # [[1.原句，2.token_list], ...]
        my_token_list = []

        # for i in utils_EN.UtilsEN.split_sentences(utils_EN.UtilsEN("english"), text):
        #     temp = []
        #     temp_token_list, _ = self.tokenizer.tokenize_by_word(i, apply_token_filters=True, with_out_filter=True)
        #     # print(temp_token_list)
        #     temp.append(i)
        #     temp.append(temp_token_list)
        #     my_token_list.append(temp)
        # start = time.time()
        # print("程序执行时间", start - start0)

        # print(my_token_list)

        return token_list, token_dict, tag_filtered_tokens, original_tokens, my_token_list

    def _generate_candidate_combine_sentence(self, text):
        """
        Accept text use the tokenizer to generate three tokenized text.
        :param text:
        :return: token_dict, tag_filtered_tokens, original_tokens
        token_list: is a syntactic unit list
        token_dict: is a syntactic unit dictionary, just removed the dupication
        original_tokens = is a list of words. not syntactic unit
        """
        assert isinstance(text, dict)

        # ---ori code---
        # # two syntatic units list, with out filters will return all the tokens, while the token list only contains token that pass certain filters.
        # token_list, token_without_filter = self.tokenizer.tokenize_by_word(text['ori_text'], apply_token_filters=True,
        #                                                                    with_out_filter=True)
        # # print(token_list)
        # # token list -> token dict {token.text, syntatic unit}
        # token_dict = SyntacticUnit.to_dict(token_list)
        #
        # # apply pos tag filters
        # # token list -> remove some by filters => tag filtered tokens
        # tag_filtered_tokens = self.tokenizer.pos_tag_filter(token_list)
        #
        # # token_with_out_filter -> original_tokens, contains all the tokens
        # original_tokens = SyntacticUnit.to_text_list(token_without_filter)
        # ---ori code---

        # 我的返回结构
        # [[1.原句，2.tag_filtered_tokens], ...]
        my_token_list = []
        token_list = []
        token_without_filter = []

        # count = 0
        for i in text['ori_list']:
            # if count % 100 == 0:
            #     print(count)
            # count += 1
            temp = []
            temp_token_list, temp_token_without_filter = self.tokenizer.tokenize_by_word(i, apply_token_filters=True,
                                                                                         with_out_filter=True)
            temp.append(i)
            temp.append(self.tokenizer.pos_tag_filter(temp_token_list))
            my_token_list.append(temp)
            token_list = token_list + temp_token_list
            token_without_filter = token_without_filter + temp_token_without_filter

        token_dict = SyntacticUnit.to_dict(token_list)
        tag_filtered_tokens = self.tokenizer.pos_tag_filter(token_list)
        original_tokens = SyntacticUnit.to_text_list(token_without_filter)

        return token_list, token_dict, tag_filtered_tokens, original_tokens, my_token_list

    # @profile(precision=4)
    def extract(self, text, ratio=0.2, words=None, position_topic_biased=WITHOUT_BIAS,
                article_structure=INVERTED_PYRAMID, return_scores=False, remove_dup_by_stem=False):
        """
        :param text:
        :param ratio:
        :param words:
        :param return_scores:
        :param position_topic_biased:
        :param article_structure:
        :param remove_dup_by_stem
        combined keywords can only use partial keywords. Our method, not limited the original keywords, but limit the
        combined keywords. that is the difference.
        :return:
        """
        if not isinstance(text, str):
            raise ValueError("Text parameter must be a Unicode object (str)!")

        token_list, token_dict, tag_filtered_tokens, original_tokens, my_token_list = self._generate_candidate(text)
        graph = graph_builder.build_word_graph(token_dict, tag_filtered_tokens, original_tokens, self.weighting)

        # PageRank cannot be run in an empty graph.
        if len(graph.nodes()) == 0:
            return []

        # Ranks the tokens using the PageRank algorithm. Returns dict of lemma -> score
        # 原来的代码
        pagerank_scores = get_page_rank_score(graph, token_list, position_topic_biased, article_structure)

        # 这里换成了my_token_list
        # pagerank_scores = my_get_page_rank_score(graph, my_token_list, position_topic_biased, article_structure, text)

        # remove the keyword after combine the keywords
        keywords = self._get_keywords(token_dict, graph, pagerank_scores, len(graph.nodes()))

        # remove keywords that has the same word stem for example: work, working, worked.
        if remove_dup_by_stem and self.language == "english":
            keywords = self.remove_dup_kw_by_stem(keywords)

        result_length = self._get_result_length(graph, pagerank_scores, ratio, words)

        return self._format_results(keywords, return_scores, result_length)

    # 生成词图后合并为句子
    # @profile(precision=4)
    def extract_combine_sentence(self, text, ratio=0.2, words=None, position_topic_biased=WITHOUT_BIAS,
                                 article_structure=INVERTED_PYRAMID, return_scores=False, remove_dup_by_stem=False):
        assert isinstance(text, dict)
        # text["ori_list"]/text["ori_text"]
        print("extract_combine_sentence")
        print("tokenize")
        token_list, token_dict, tag_filtered_tokens, original_tokens, my_token_list = self._generate_candidate_combine_sentence(
            text)
        # print(my_token_list)
        graph = graph_builder.build_word_graph(token_dict, tag_filtered_tokens, original_tokens, self.weighting)
        print("page_rank")
        pagerank_scores = get_page_rank_score_combine_sentence(graph, token_list, position_topic_biased,
                                                               article_structure, my_token_list)

        sorted_keys = sorted(pagerank_scores, key=pagerank_scores.get, reverse=True)
        value_rank = {key: rank for rank, key in enumerate(sorted_keys, 1)}

        filter_data = [(index, key, pagerank_scores[key], value_rank[key]) for index, key in
                       enumerate(text["ori_list"])]

        return filter_data

    def remove_dup_kw_by_stem(self, keywords):
        rm_dup_keywords = {}
        dup_checker = set()
        for keyword, score in keywords.items():
            stemmed_word = self.tokenizer.utils.stem_sentence(keyword)
            if stemmed_word not in dup_checker:
                dup_checker.add(stemmed_word)
                rm_dup_keywords[keyword] = score

        return rm_dup_keywords

    def _get_result_length(self, graph, pagerank_scores, ratio, words):
        lemmas = graph.nodes()
        lemmas.sort(key=lambda s: pagerank_scores[s], reverse=True)
        result_length = len(lemmas) * ratio if words is None else words
        return int(result_length)

    def _get_keywords(self, token_dict, graph, pagerank_scores, result_length):
        lemmas = graph.nodes()
        lemmas.sort(key=lambda s: pagerank_scores[s], reverse=True)
        # compute result length
        extracted_lemmas = [(pagerank_scores[lemmas[i]], lemmas[i],) for i in range(result_length)]

        lemmas_to_word = _lemmas_to_words(token_dict)

        keywords = {}
        for score, lemma in extracted_lemmas:
            keyword_list = lemmas_to_word[lemma]
            # all the words with the same word original shared the same score. no effect for chinese.
            for keyword in keyword_list:
                keywords[keyword] = score

        return keywords

    def _format_results(self, keyword_scores, return_scores, result_length):
        """
        :param _keywords:dict of keywords:scores
        :param combined_keywords:list of word/s
        """
        keywords = sorted(keyword_scores.keys(), key=lambda w: keyword_scores[w], reverse=True)
        keywords = keywords[0:result_length]
        if return_scores:
            return [(word, keyword_scores[word]) for word in keywords]
        return keywords
