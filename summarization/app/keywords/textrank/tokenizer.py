from abc import ABC, abstractmethod
import summarization.app.utils as utils_factory
from summarization.app.keywords.textrank.syntactic_unit import SyntacticUnit
from summarization.app.utils.utils_CN import UtilsCN
from summarization.app.web_api.autophrase_api import generating_list


class Tokenizer(ABC):
    @staticmethod
    def factory(language):
        """
        A Factory function for Tokenizer.
        :param language: english or chinese
        :param candidate_generation_method: candidate_generation_method Name
        :return: A candidate_generation method
        """
        # parser_name = ap means this parse all the articles doc name starts with AP
        if language == "english":
            return TokenizerEN()
        if language == "chinese":
            return TokenizerCN()
        else:
            # Parser for other format hasn't been writen yet
            assert 0, "bad weighting method request: " + language

    @abstractmethod
    def tokenize_by_word(self, text, apply_token_filters=True, customize_token_filters=None, with_out_filter=False):
        raise NotImplementedError

    @abstractmethod
    def tokenize_by_phrase(self, text, apply_token_filters=True, customize_token_filters=None, with_out_filter=False):
        raise NotImplementedError

    @abstractmethod
    def tokenize_by_sentence(self, text, apply_token_filters=True, customize_token_filters=None):
        raise NotImplementedError

    @abstractmethod
    def pos_tag_filter(self, units_list, include_tags=None, exclude_tags=None):
        raise NotImplementedError


class TokenizerEN(Tokenizer):
    def __init__(self):
        self.utils = utils_factory.factory("english")

    def tokenize_by_word(self, text, apply_token_filters=True, customize_token_filters=None, with_out_filter=False):
        original_words = self.utils.tokenize(text)

        filtered_words = None
        if apply_token_filters:
            filtered_words = self.utils.tokens_filter(original_words, customize_filters=customize_token_filters)

        tags = self.utils.tagger(original_words)

        units = SyntacticUnit.merge_syntactic_units(original_words, filtered_words, tags)

        if with_out_filter:
            units_without_filter = SyntacticUnit.merge_syntactic_units(original_words)
            return units, units_without_filter
        return units

    def tokenize_by_sentence(self, text, apply_token_filters=True, customize_token_filters=None):
        original_sentences = self.utils.split_sentences(text)

        filtered_sentences = None
        if apply_token_filters:
            filtered_sentences = self.utils.tokens_filter(original_sentences, customize_filters=customize_token_filters)

        units = SyntacticUnit.merge_syntactic_units(original_sentences, filtered_sentences)
        return units

    def pos_tag_filter(self, units_list, include_tags=None, exclude_tags=None):
        if not include_tags:
            include_tags = ['NN', 'JJ']

        if not exclude_tags:
            exclude_tags = []

        include_filters = frozenset(include_tags)
        exclude_filters = frozenset(exclude_tags)
        if include_filters and exclude_filters:
            raise ValueError("Can't use both include and exclude filters, should use only one")

        result = []
        for unit in units_list:
            if exclude_filters and unit.tag in exclude_filters:
                continue
            if (include_filters and unit.tag in include_filters) or not include_filters or not unit.tag:
                result.append(unit.token)
        return list(set(result))

    def tokenize_by_phrase(self, text, apply_token_filters=True, customize_token_filters=None, with_out_filter=False):
        return


class TokenizerCN(Tokenizer):
    def __init__(self):
        self.utils = UtilsCN(language="chinese")

    def tokenize_by_word(self, text, apply_token_filters=True, customize_token_filters=None, with_out_filter=False):
        original_words = self.utils.tokenize(text)

        filtered_words = None
        if apply_token_filters:
            filtered_words = self.utils.tokens_filter(original_words, customize_filters=customize_token_filters)

        tags = self.utils.tagger(text)

        units = SyntacticUnit.merge_syntactic_units(original_words, filtered_words, tags)
        units_without_filter = SyntacticUnit.merge_syntactic_units(original_words)

        return units, units_without_filter

    def pos_tag_filter(self, units_list, include_tags=None, exclude_tags=None):
        if not include_tags:
            include_tags = ['ns', 'n', 'vn', 'v']

        if not exclude_tags:
            exclude_tags = []

        include_filters = frozenset(include_tags)
        exclude_filters = frozenset(exclude_tags)
        if include_filters and exclude_filters:
            raise ValueError("Can't use both include and exclude filters, should use only one")

        result = []
        for unit in units_list:
            if exclude_filters and unit.tag in exclude_filters:
                continue
            if (include_filters and unit.tag in include_filters) or not include_filters or not unit.tag:
                result.append(unit.token)
        return list(set(result))

    def tokenize_by_sentence(self, text, apply_token_filters=True, customize_token_filters=None):
        original_sentences = self.utils.split_sentences(text)

        filtered_sentences = None
        if apply_token_filters:
            filtered_sentences = self.utils.tokens_filter(original_sentences, customize_filters=customize_token_filters)

        units = SyntacticUnit.merge_syntactic_units(original_sentences, filtered_sentences)
        return units

    def tokenize_by_phrase(self, text, apply_token_filters=True, customize_token_filters=None, with_out_filter=False):
        return
