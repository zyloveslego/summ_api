import unittest
from app.summ.model.evaluation.summary_evaluation import evaluate


class TestSummeval(unittest.TestCase):

    def test_evaluate(self):
        rouge_1, rouge_2, rouge_l = evaluate(
            summary="I'm living New York its my home town so awesome",
            reference=["My home town is awesome"])
        self.assertAlmostEqual(0.749, rouge_1, delta=0.01)
        self.assertAlmostEqual(0.666, rouge_2, delta=0.01)
        self.assertAlmostEqual(0.749, rouge_l, delta=0.01)


if __name__ == '__main__':
    unittest.main()