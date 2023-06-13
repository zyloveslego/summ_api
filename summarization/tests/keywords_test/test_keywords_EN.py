from app.keywords.keyword import KeyWord
import unittest
import os


# function for get test data
def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestKeywords(unittest.TestCase):
    def setUp(self):
        self.extractor = KeyWord.basic_init(language="english")

    def test_text_keywords(self):
        text = get_text_from_test_data("mihalcea_tarau.txt")

        # Calculate keywords
        generated_keywords = self.extractor.extract(text, ratio=1, return_scores=True, position_topic_biased=1, article_structure=1)

        # To be compared to the reference.
        # reference_keywords = get_text_from_test_data("mihalcea_tarau.kw.txt").split("\n")
        print(generated_keywords)

        # self.assertEqual({str(x) for x in reference_keywords}, {str(x) for x in generated_keywords})

    def test_keywords_few_distinct_words_is_empty_string(self):
        text = get_text_from_test_data("few_distinct_words.txt")
        self.assertEqual(self.extractor.extract(text), "")

    def test_keywords_few_distinct_words_split_is_empty_list(self):
        text = get_text_from_test_data("few_distinct_words.txt")
        self.assertEqual(self.extractor.extract(text, split=True), [])

    def test_text_summarization_on_short_input_text_and_split_is_not_empty_list(self):
        text = get_text_from_test_data("unrelated.txt")

        # Keeps the first 8 sentences to make the text shorter.
        text = "\n".join(text.split('\n')[:8])

        self.assertNotEqual(self.extractor.extract(text, split=True), [])

    def test_text_summarization_on_short_input_text_is_not_empty_string(self):
        text = get_text_from_test_data("unrelated.txt")

        # Keeps the first 8 sentences to make the text shorter.
        text = "\n".join(text.split('\n')[:8])

        self.assertNotEqual(self.extractor.extract(text, split=True), "")

    def test_keywords_ratio(self):
        text = get_text_from_test_data("mihalcea_tarau.txt")

        # Check ratio parameter is well behaved.
        # Because length is taken on tokenized clean text we just check that
        # ratio 40% is twice as long as ratio 20%
        selected_docs_20 = self.extractor.extract(text, ratio=0.2, split=True, combination=True)
        selected_docs_40 = self.extractor.extract(text, ratio=0.4, split=True, combination=True)

        self.assertAlmostEqual(float(len(selected_docs_40)) / len(selected_docs_20), 0.4 / 0.2, delta=0.3)

    def test_keywords_consecutive_keywords(self):
        text = "Rabbit populations known to be plentiful, large, and diverse \
                in the area. \
                Adjacent to the site, a number number well over a thousand. \
                The number of these rabbit populations has diminished in recent \
                years, and perhaps we have become number to a number of their \
                numbers numbering fewer."

        # Should not raise an exception.
        self.assertIsNotNone(self.extractor.extract(text,  words=10))

    def test_remove_dup_by_stem(self):
        text = "Rabbit populations known to be plentiful, large, and diverse \
                in the area. \
                Adjacent to the site, a number number well over a thousand. \
                The number of these rabbit populations has diminished in recent \
                years, and perhaps we have become number to a number of their \
                numbers numbering fewer."

        # Should the second print should remove numbers, the first should print both "number and numbers"
        print(self.extractor.extract(text, words=10))
        print("*" * 10)
        print(self.extractor.extract(text, words=10, remove_dup_by_stem=True))
        pass

    def test_repeated_keywords(self):
        text = get_text_from_test_data("repeated_keywords.txt")

        kwds = self.extractor.extract(text)
        self.assertTrue(len(kwds.splitlines()))


if __name__ == '__main__':
    unittest.main()
