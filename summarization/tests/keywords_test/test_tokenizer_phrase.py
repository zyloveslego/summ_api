from app.keywords.textrank.tokenizer import Tokenizer
import unittest
import os


# function for get test data
def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestTokenizerPhrase(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer.factory("english", "PHRASE")

    def test_text_keywords(self):
        text = get_text_from_test_data("mihalcea_tarau.txt")

        # Calculate keywords
        generated_keywords = self.tokenizer.tokenize_by_word(text)


if __name__ == '__main__':
    unittest.main()
