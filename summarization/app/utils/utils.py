from abc import ABC, abstractmethod
from .stopwords import get_stopwords_by_language
from functools import wraps
import time


class Utils(ABC):
    def __init__(self, language):
        self.language = language
        self.stopwords = self._set_stopwords()

    @abstractmethod
    def stem_sentence(self, sentence):
        raise NotImplementedError

    @abstractmethod
    def get_stopwords_list(self):
        raise NotImplementedError

    @abstractmethod
    def strip_stopwords(self, sentence):
        raise NotImplementedError

    @abstractmethod
    def strip_numeric(self, sentence):
        raise NotImplementedError

    @abstractmethod
    def strip_punctuation(self, sentence):
        raise NotImplementedError

    @abstractmethod
    def split_sentences(self, text):
        raise NotImplementedError

    @abstractmethod
    def split_para(self, text):
        raise NotImplementedError

    @abstractmethod
    def tokenize(self, text):
        raise NotImplementedError

    @abstractmethod
    def tokens_filter(self, tokens, customize_filters=None):
        raise NotImplementedError

    @abstractmethod
    def tagger(self, tokens):
        raise NotImplementedError

    @abstractmethod
    def word_count(self, sentence):
        raise NotImplementedError

    def _set_stopwords(self):
        words = get_stopwords_by_language(self.language)
        return frozenset(w for w in words.split() if w)

    def to_unicode(self, text, encoding='utf8', errors='strict'):
        """Convert `text` to unicode.
        Parameters
        ----------
        text : str
            Input text.
        errors : str, optional
            Error handling behaviour, used as parameter for `unicode` function (python2 only).
        encoding : str, optional
            Encoding of `text` for `unicode` function (python2 only).
        Returns
        -------
        str
            Unicode version of `text`.
        """
        if isinstance(text, str):
            return text
        return str(text, encoding, errors=errors)


def timing(method):
    @wraps
    def wrap(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return wrap
