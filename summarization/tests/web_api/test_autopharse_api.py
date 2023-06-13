import unittest
import os
from app.web_api.autophrase_api import generating_list


def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestUtilsCN(unittest.TestCase):
    def test_tokenize_CN(self):
        text = get_text_from_test_data("pyramid.txt")
        phrase_list = generating_list(text)


if __name__ == '__main__':
    unittest.main()
