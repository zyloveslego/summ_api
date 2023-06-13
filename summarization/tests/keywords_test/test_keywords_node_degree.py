from app.keywords.keyword import KeyWord
import unittest
import os
import app.keywords.textrank.graph.graph_builder as graph_builder
import app.keywords.textrank.weighting as Weighting
from app.keywords.textrank.syntactic_unit import SyntacticUnit
from app.keywords.textrank.tokenizer import Tokenizer


# function for get test data
def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestKeywords(unittest.TestCase):
    def setUp(self):
        self.extractor = Degree.basic_init(language="english", weighting_method="CO_OCCUR_W2V")

    def test_degree(self):
        text = get_text_from_test_data("pyramid.txt")
        self.extractor = self.extractor.extract(text)


class Degree(object):
    def __init__(self, language, tokenizer, weighting, candidate_generation_method="WORD"):
        """
        :param language: english or chines
        :param tokenizer:
        :param weighting:
        :param combinator:
        """
        self.language = language
        self.tokenizer = tokenizer
        self.weighting = weighting
        self.phrase_or_words = candidate_generation_method

    @classmethod
    def basic_init(cls, language, candidate_generation_method="WORD", weighting_method="CO_OCCUR"):
        """
        :param language: english or chines
        :param candidate_generation_method: WORD means use only words, PHRASE is not available here
        :param weighting_method: See Weighing package for detail.
        """
        tokenizer = Tokenizer.factory(language)
        weighting = Weighting.factory(language, weighting_method, word_or_sentence="WORD")
        return cls(language, tokenizer, weighting, candidate_generation_method)

    def _generate_candidate(self, text):
        """
        Accept text use the tokenizer to generate three tokenized text.
        :param text:
        :return: token_dict, tag_filtered_tokens, original_tokens
        token_list: is a syntactic unit list
        token_dict: is a syntactic unit dictionary, just removed the dupication
        original_tokens = is a list of words. not syntactic unit
        """
        token_list, token_without_filter = self.tokenizer.tokenize_by_word(text, apply_token_filters=True, with_out_filter=True)
        token_dict = SyntacticUnit.to_dict(token_list)

        # apply tag filters
        tag_filtered_tokens = self.tokenizer.pos_tag_filter(token_list)

        original_tokens = SyntacticUnit.to_text_list(token_without_filter)

        return token_list, token_dict, tag_filtered_tokens, original_tokens

    def extract(self, text):
        """
        :param text:
        :param ratio:
        :param words:
        :param split:
        :param scores:
        :param combination:
        :param textrank_original:  when generate keywords, texrank method apply the ratio and words there, so the
        combined keywords can only use partial keywords. Our method, not limited the original keywords, but limit the
        combined keywords. that is the difference.
        :return:
        """
        if not isinstance(text, str):
            raise ValueError("Text parameter must be a Unicode object (str)!")

        if self.phrase_or_words == "PHRASE":
            combination = False

        token_list, token_dict, tag_filtered_tokens, original_tokens = self._generate_candidate(text)
        graph = graph_builder.build_word_graph(token_dict, tag_filtered_tokens, original_tokens, self.weighting)
        for node, neighbors in sorted(graph.node_neighbors.items()):
            print(node, len(neighbors))
        return graph


if __name__ == '__main__':
    unittest.main()
