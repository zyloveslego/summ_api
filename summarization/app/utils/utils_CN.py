from .utils import Utils
import jieba.posseg
import jieba
import re

RE_SENTENCE_CN = re.compile('(\S.+?[?!;~。？！；～])|(\S.+?)(?=[\n]|$)')
punctuation = r"""。！？，@￥%……（）!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""


class UtilsCN(Utils):
    def __init__(self, language):
        super().__init__(language)

    def stem_sentence(self, sentence):
        pass

    def get_stopwords_list(self):
        return self.stopwords

    def strip_stopwords(self, sentence):
        # need text split with " "
        return " ".join(w for w in sentence.split() if w not in self.stopwords)

    def strip_numeric(self, sentence):
        re_numeric = re.compile(r"[0-9]+", re.UNICODE)
        return re_numeric.sub("", sentence)

    def strip_punctuation(self, sentence):
        re_punctuation = re.compile('([%s])+' % re.escape(punctuation), re.UNICODE)
        return re_punctuation.sub(" ", sentence)

    def split_sentences(self, text):
        return [sentence for sentence in _get_sentences(text)]

    def split_para(self, text):
        return [para for para in _get_para(text)]

    def tokenize(self, text):
        return list(jieba.cut(text))

    def tokens_filter(self, tokens, customize_filters=None):
        def apply_filters_to_token(token):
            for f in filters:
                token = f(token)
            return token

        if customize_filters:
            filters = customize_filters
            return list(map(apply_filters_to_token, tokens))
        else:
            filters = [lambda x: x, self.strip_numeric, self.strip_punctuation, self.strip_stopwords]
            return list(map(apply_filters_to_token, tokens))

    def tagger(self, tokens):
        tag_list = []
        words = jieba.posseg.dt.cut(tokens)
        # count = 0
        for word, flag in words:
            tag_list.append((word, flag))
            # print(word, flag)
            # count = count + 1
            # if count % 10000 == 0:
            #     print(count)
        return tag_list

    def word_count(self, sentence):
        return len(sentence)


def _get_para(text):
    return re.split("\r\n|\n", text)


def _get_sentences(text):
    for match in RE_SENTENCE_CN.finditer(text):
        yield match.group()
