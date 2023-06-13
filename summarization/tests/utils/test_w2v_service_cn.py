from app.utils.tovec_service import ToVecService
import unittest


class TestW2VService(unittest.TestCase):
    def setUp(self):
        self.to_vec_service = ToVecService.set_default_by_language("chinese")

    def test_cn_word_similarity(self):
        w1 = "国王"
        w2 = "皇帝"
        similarity = self.to_vec_service.word_similarity(w1, w2)
        self.assertAlmostEqual(1, similarity, delta=0.2)


if __name__ == '__main__':
    unittest.main()
