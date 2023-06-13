import unittest
import jieba.analyse
from app.keywords.keyword import KeyWord
import os


# function for get test data
def get_text_from_test_data(file):
    pre_path = os.path.join(os.path.dirname(__file__), 'test_data')
    with open(os.path.join(pre_path, file), mode='r') as f:
        return f.read()


class TestKeywords(unittest.TestCase):
    def setUp(self):
        self.extractor = KeyWord.basic_init(language="chinese")

    def test_keywords_consecutive_keywords(self):
        text = "据《纽约时报》报道，当地时间9日，美国联邦调查局（FBI）突击搜查了特朗普私人律" \
               "师迈克尔·科恩（Michael Cohen）的办公室，缴获了电子邮件、税务文件和业务记录等资料。" \
               "据悉，FBI的调查内容还包括科恩向一名女艳星的汇款记录，该演员此前曾声称与特朗普有染。不过，" \
               "几天前，特朗普曾否认了解付款一事。据报道，FBI是在美国特别检察官罗伯特·米勒的指导下对科恩的办公室进行了搜查。"

        # Should not raise an exception.
        expected = ['业务记录', '税务文件', '办公室', '突击搜查', '电子邮件', '报道', '演员', '包括', '检察官', '调查内容',
                    '美国', '汇款', '声称', '私人律师', '缴获', '进行', '艳星', '资料', '有染', '时间']
        # equal without order
        self.assertCountEqual(expected, self.extractor.extract(text, ratio=1, combination=True))

    def test_keywords_jieba(self):
        text = "据《纽约时报》报道，当地时间9日，美国联邦调查局（FBI）突击搜查了特朗普私人律" \
               "师迈克尔·科恩（Michael Cohen）的办公室，缴获了电子邮件、税务文件和业务记录等资料。" \
               "据悉，FBI的调查内容还包括科恩向一名女艳星的汇款记录，该演员此前曾声称与特朗普有染。不过，" \
               "几天前，特朗普曾否认了解付款一事。据报道，FBI是在美国特别检察官罗伯特·米勒的指导下对科恩的办公室进行了搜查。"
        expected = ['记录', '搜查', '税务', '付款', '一事', '办公室', '调查', '电子邮件', '报道', '业务', '文件',
                    '演员', '私人', '美国', '检察官', '否认', '了解', '汇款', '据悉', '声称']
        self.assertCountEqual(expected, jieba.analyse.textrank(text))

    def test_keywords_extract(self):
        text = get_text_from_test_data("news.txt")
        # Should not raise an exception.
        expected = ['台湾', '出席', '民族大义', '根本利益', '机遇', '会见', '时代', '愿意继续', '中国特色', '进入', '先生',
                    '亚洲论坛', '共同市场基金会', '祖国和平统一', '坚持', '推动两岸关系', '希望', '同胞', '台胞', '海南',
                    '一家亲', '经济文化交流', '董事长', '表示', '共识', '获得', '梦', '台独', '欢迎']
        self.assertCountEqual(expected, self.extractor.extract(text, ratio=1, combination=True))

    def test_keywords_extract_(self):
        text = get_text_from_test_data("news.txt")
        # Should not raise an exception.
        expected = ['发展', '台湾', '合作', '朋友', '工商界', '出席', '台湾同胞', '分享', '时代', '进程',
                    '祖国', '机遇', '继续', '大陆', '进入', '社会主义', '会见', '大计', '亚洲', '希望']
        self.assertCountEqual(expected, jieba.analyse.textrank(text))


if __name__ == '__main__':
    unittest.main()
