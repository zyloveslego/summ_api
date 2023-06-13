from app.utils.tovec_service import ToVecService
from app import definitions
import unittest
from itertools import combinations as _combinations
import time


def get_combinations(words_list):
    for combo in _combinations(words_list, 2):
        yield combo


text = "Rabbit populations known to be plentiful large and diverse in the area Adjacent to the site " \
       "a number number well over a thousand The number of these rabbit populations has diminished in recent " \
       "years and perhaps we have become number to a number of their numbers numbering fewer Hurricane " \
       "Gilbert swept toward the Dominican Republic Sunday and the Civil Defense alerted its heavily " \
       "populated south coast to prepare for high winds heavy rains and high seas Cabral said residents of " \
       "the province of Barahona should closely follow Gilbert's movement Florence the sixth named storm of " \
       "the Atlantic storm season was the second hurricane The first Debby reached minimal hurricane strength " \
       "briefly before hitting the Mexican coast last month An estimated people live in the province including " \
       "in the city of Barahona about miles west of Santo Domingo A few weeks ago it felt as if a trade war " \
       "pitting the United States against allies like Australia Canada and the European Union was over before " \
       "it even began The Trump administration dispensed so many temporary exemptions to steel and aluminum " \
       "tariffs that many countries figured the threats were just political theater But with only days left " \
       "before the exemptions expire and punitive tariffs take effect dawning on foreign leaders that decades " \
       "of warm relations with the United States carry little weight with a president dismissive of diplomatic " \
       "norms and hostile toward the ground rules of international trade"


class TestW2VService(unittest.TestCase):
    def setUp(self):
        self.to_vec_service = ToVecService.set_default_by_language("english")

    def test_en_word_similarity(self):
        w1 = "king"
        w2 = "queen"
        similarity = self.to_vec_service.word_similarity(w1, w2)
        self.assertAlmostEqual(1, similarity, delta=0.3)

    def test_api(self):
        print("start!!!!!!!")
        start = time.time()
        word_list = list(set(text.lower().split(" ")))
        combo_generator = get_combinations(word_list)
        for w1, w2 in combo_generator:
            a = self.to_vec_service.word_similarity(w1, w2)
            print(w1, w2, a)
        end = time.time()
        print(end - start)

    def test_en_wmd(self):
        print("start!!!!!!!")
        start = time.time()
        s1 = "Nice place to take a date at a reasonable price."
        s2 = "Reasonable prices. Makes for a nice dinner out in the town."
        a = self.to_vec_service.sentence_similarity(s1, s2)
        end = time.time()
        print(end - start)
        print(a)


if __name__ == '__main__':
    unittest.main()
