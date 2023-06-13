from app.keywords.keysentence import KeySentence
import unittest
import os
from app.summ.model.ks_summarizer import sentence_rank


# function for get test data
def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestKeywords(unittest.TestCase):
    def setUp(self):
        self.extractor = KeySentence.basic_init(language="english")
        self.sen_extractor = sentence_rank

    def test_text_keywords(self):
        text = get_text_from_test_data("pyramid.txt")

        # Calculate keywords
        generated_sentences = self.extractor.extract(text, ratio=1, return_scores=True, position_topic_biased=1, article_structure=2)
        generated_sentences.sort(key=lambda x: x[1], reverse=True)
        for sentence in generated_sentences:
            print(sentence)
        # print("--------------")
        # x = self.sen_extractor(text)
        # x.sort(key=lambda s: s.score, reverse=True)
        # for i in x:
        #     print(i.text, i.score)

if __name__ == '__main__':
    unittest.main()
