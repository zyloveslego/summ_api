import unittest
from app.summ.model.kw_summarizer import KWSummarizer
from app.keywords.keyword import KeyWord
import os


def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestKWSummarizerCN(unittest.TestCase):

    def setUp(self):
        self.customized_textrank = KeyWord.basic_init(language="chinese", weighting_method="CO_OCCUR")
        self.summarizer = KWSummarizer.factory(language="chinese", summarizer_name="TW", customized_textrank=self.customized_textrank)

    def test_summary(self):
        text = get_text_from_test_data("news_cn_2.txt")
        print(self.customized_textrank.extract(text, ratio=0.7, position_biased=True, combination=False))
        summary = self.summarizer.summarize(text, sentence_ratio=0.80)
        print("\n".join(summary))
        pass

    def test_summary_para_formater(self):
        text = get_text_from_test_data("news_cn.txt")
        summary = self.summarizer.summarize(text, sentence_ratio=0.10)
        print("".join(self.summarizer.format_result_by_para(text, summary)))
        pass

    def test_cn_score(self):
        text = get_text_from_test_data("news_cn.txt")
        summary = self.summarizer.summarize(text, sentence_ratio=0.3, score=True)
        print(summary)
        pass


if __name__ == '__main__':
    unittest.main()
