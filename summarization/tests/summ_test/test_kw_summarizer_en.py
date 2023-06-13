import unittest
from summarization.app.summ.model.kw_summarizer import KWSummarizer
from summarization.app.keywords.keyword import KeyWord
import os


def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestKWSummarizerCN(unittest.TestCase):

    def setUp(self):
        self.customized_textrank = KeyWord.basic_init(language="english", weighting_method="CO_OCCUR")
        self.summarizer = KWSummarizer.factory(language="english", summarizer_name="CTW", customized_textrank=self.customized_textrank)

    def test_summary_score(self):
        text = get_text_from_test_data("text03.txt")
        # print(self.customized_textrank.extract(text, ratio=1, return_scores=True, position_topic_biased=1, article_structure=2))
        summary = self.summarizer.summarize(text, sentence_ratio=1, show_score=True, show_ranking=True)
        # summary = [(k, i, j) for i, j, k in summary]
        # summary = sorted(summary, reverse=False, key=lambda x:x[0])
        # print('------first test--------')
        # for ele in summary:
        #     print(type(ele))
        #     print('------ele------')
        #     print(ele)
        summary.sort(key=lambda x: x[2], reverse=True)
        # print(summary)

        for ele in summary:
            print(ele)
        pass

    def test_summary_para_formater(self):
        text = get_text_from_test_data("news_en.txt")
        summary = self.summarizer.summarize(text, sentence_ratio=0.20)
        print('------second test--------')
        for ele in summary:
            print('------ele------')
            print(ele)
        print('---------second tests-----------')
        print("".join(self.summarizer.format_result_by_para(text, summary)))
        print('--------second tests---------')
        pass


if __name__ == '__main__':
    unittest.main()
