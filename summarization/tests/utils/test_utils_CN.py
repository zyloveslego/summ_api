from app.utils.utils_CN import UtilsCN
import unittest
import os


def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestUtilsCN(unittest.TestCase):
    def setUp(self):
        self.utils = UtilsCN(language="chinese")

    def test_tokenize_CN(self):
        text = "你好，我今天觉得很好。"
        expect_tokens = ["你好", "，", "我", "今天", "觉得", "很", "好", "。"]
        tokens_generator = self.utils.tokenize(text)
        self.assertEqual(expect_tokens, [x for x in tokens_generator])

    def test_split_sentence_CN(self):
        text = "你好。这不是一个句子。而是好几个句子！究竟有多少句子?"
        expect = ["你好。", "这不是一个句子。", "而是好几个句子！","究竟有多少句子?"]
        sentences = self.utils.split_sentences(text)
        self.assertEqual(expect, sentences)

    def test_strip_punctuation(self):
        text = "你好。这不是一个句子。而是好几个句子！究竟有多少句子?"
        expect = "你好 这不是一个句子 而是好几个句子 究竟有多少句子 "
        punctuation_removed_text = self.utils.strip_punctuation(text)
        self.assertEqual(expect, punctuation_removed_text)

    def test_split_sentences(self):
        text = "你好。这不是一个句子。而是好几个句子！究竟有多少句子?"
        expect = ["你好。", "这不是一个句子。", "而是好几个句子！", "究竟有多少句子?"]
        sentences = self.utils.split_sentences(text)
        self.assertEqual(expect, sentences)

    def test_strip_stopwords(self):
        text = "你好，我今天觉得很好。"
        text = " ".join(self.utils.tokenize(text))
        expect = "你好 今天 觉得 好"
        sentences = self.utils.strip_stopwords(text)
        self.assertEqual(sentences, expect)

    def test_tagger(self):
        pass

    def test_split_para(self):
        text = get_text_from_test_data("news_cn.txt")
        print(self.utils.split_para(text))


if __name__ == '__main__':
    unittest.main()
