import unittest
from app.utils.utils_EN import UtilsEN


class TestUtilsEN(unittest.TestCase):
    def setUp(self):
        self.utils = UtilsEN(language="english")

    def test_tokenize(self):
        text = "Hi, I feel good today."
        expect_tokens = ["hi", "i", "feel", "good", "today"]
        tokens = self.utils.tokenize(text)
        self.assertEqual(expect_tokens, tokens)

    def test_tokenize_EN(self):
        text = "Hi, I feel good today."
        expect_tokens = ["hi", "i", "feel", "good", "today"]
        tokens = self.utils.tokenize(text)
        self.assertEqual(expect_tokens, tokens)

    # def test_replace_abbreviations(self):
    #     text = "hello, P.S."
    #     processed = self.utils._replace_abbreviations(text)
    #     self.assertEqual(processed, "hello, Mr.@Zhang.")

    def test_split_sentence_EN(self):
        text = "hi. These are sentences. It contains several sentences! How many sentences are there?"
        expect = ["hi.", "These are sentences.", "It contains several sentences!", "How many sentences are there?"]
        sentences = self.utils.split_sentences(text)
        self.assertEqual(expect, sentences)

    def test_tagger(self):
        text = "Hi, I feel good today."
        expect_tokens = [('hi', 'NN'), ('i', 'NN'), ('feel', 'VBP'), ('good', 'JJ'), ('today', 'NN')]
        tokens = self.utils.tokenize(text)
        pos_tagged = self.utils.tagger(tokens)
        self.assertEqual(expect_tokens, pos_tagged)


if __name__ == '__main__':
    unittest.main()
