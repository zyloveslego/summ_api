import re
import unicodedata
import string
import nltk
nltk.download('averaged_perceptron_tagger')
from .utils import Utils
from summarization.app.utils.snowball import SnowballStemmer
from nltk.data import load

PAT_ALPHABETIC = re.compile(r'(((?![\d])\w)+)', re.UNICODE)
# RE_SENTENCE_EN - Pattern to split text to sentences.
# RE_SENTENCE_EN = re.compile('(\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)')

AB_ACRONYM_LETTERS = re.compile("([a-zA-Z])\.([a-zA-Z])\.")

# SEPARATOR - Special separator used in abbreviations.
# SEPARATOR = r"@"
# Used for English sentence split remove the abbreviation to get accurate sentence split
# AB_SENIOR - Pattern for detecting abbreviations (example: Sgt. Pepper).
# AB_SENIOR = re.compile("([A-Z][a-z]{1,2}\.)\s(\w)")
# AB_ACRONYM - Pattern for detecting acronyms.(P.S. This is)
# AB_ACRONYM = re.compile("(\.[a-zA-Z]\.)\s(\w)")
# UNDO_AB_SENIOR - Pattern like AB_SENIOR but with SEPARATOR between abbreviation and next word.
# UNDO_AB_SENIOR = re.compile("([A-Z][a-z]{1,2}\.)" + SEPARATOR + "(\w)")
# UNDO_AB_ACRONYM - Pattern like AB_ACRONYM but with SEPARATOR between abbreviation and next word.
# UNDO_AB_ACRONYM = re.compile("(\.[a-zA-Z]\.)" + SEPARATOR + "(\w)")


class UtilsEN(Utils):
    def __init__(self, language):
        super().__init__(language)
        self.stemmer = SnowballStemmer("english")

    def stem_sentence(self, sentence):
        word_stems = [self.stemmer.stem(word) for word in sentence.split()]
        return " ".join(word_stems)

    def get_stopwords_list(self):
        return self.stopwords

    def split_sentences(self, text):
        # sentence_list = nltk.sent_tokenize(text)
        sentence_list = []

        # from nltk.data import load
        tokenizer = load('tokenizers/punkt/{0}.pickle'.format('english'))
        paragraphs = [p for p in text.split('\n') if p]
        for paragraph in paragraphs:
            sentence_list.extend(tokenizer.tokenize(paragraph))
        return sentence_list

        # split title from the text
        # title does not have a punctuation, so title will stick with the first sentence.
        if sentence_list and "\r\n" in sentence_list[0] or "\n" in sentence_list[0]:
            if "\r\n" in sentence_list:
                title_sentence_split = [sen for sen in sentence_list[0].split("\r\n") if sen]
            else:
                title_sentence_split = [sen for sen in sentence_list[0].split("\n") if sen]
            sentence_list = title_sentence_split + sentence_list[1:]

        return [_trim(sentence) for sentence in sentence_list]

    def tokenize(self, text):
        text_without_acronyms = replace_with_separator(text, "", [AB_ACRONYM_LETTERS])
        text = super().to_unicode(text_without_acronyms, encoding="utf8", errors="strict")
        return tokenize(text, lowercase=True, deacc=False)

    def strip_stopwords(self, sentence):
        return " ".join(w for w in sentence.split() if w not in self.stopwords)

    def strip_punctuation(self, sentence):
        re_punctuation = re.compile('([%s])+' % re.escape(string.punctuation), re.UNICODE)
        return re_punctuation.sub(" ", sentence)

    def strip_numeric(self, sentence):
        re_numeric = re.compile(r"[0-9]+", re.UNICODE)
        return re_numeric.sub("", sentence)

    def tokens_filter(self, tokens, customize_filters=None):
        def apply_filters_to_token(token):
            for f in filters:
                token = f(token)
            return token

        if customize_filters:
            filters = customize_filters
            return list(map(apply_filters_to_token, tokens))
        else:
            filters = [lambda x: x.lower(), self.strip_numeric,
                       self.strip_punctuation, self.strip_stopwords, self.stem_sentence]
            return list(map(apply_filters_to_token, tokens))

    def tagger(self, tokens):
        return nltk.pos_tag(tokens)

    def word_count(self, sentence):
        return len(sentence.split(" "))

    def split_para(self, text):
        return [para for para in _get_para(text)]


def _trim(text):
    text = text.replace('\r\n', '')
    text = text.replace('\n', '')
    text = text.strip()
    return text


def _get_para(text):
    return re.split("\r\n|\n", text)


def tokenize(text, lowercase=False, deacc=False):
    """Iteratively yield tokens as unicode strings, removing accent marks and optionally lowercasing string
    if any from `lowercase`, `to_lower`, `lower` set to True.
    Parameters
    ----------
    text : str
        Input string.
    lowercase : bool, optional
        If True - lowercase input string.
    deacc : bool, optional
        If True - remove accentuation from string by :func:`~gensim.utils.deaccent`.
    Yields
    ------
    str
        Contiguous sequences of alphabetic characters (no digits!), using :func:`~gensim.utils.simple_tokenize`
    Examples
    --------
    >>> from app.utils.utils_EN import tokenize
    >>> list(tokenize('Nic nemůže letět rychlostí vyšší, než 300 tisíc kilometrů za sekundu!', deacc=True))
    [u'Nic', u'nemuze', u'letet', u'rychlosti', u'vyssi', u'nez', u'tisic', u'kilometru', u'za', u'sekundu']
    """
    if lowercase:
        text = text.lower()
    if deacc:
        text = deaccent(text)
    return [token for token in simple_tokenize(text)]


def simple_tokenize(text):
    """Tokenize input test using :const:`gensim.utils.PAT_ALPHABETIC`.
    remove punctuation
    Parameters
    ----------
    text : str
        Input text.
    Yields
    ------
    str
        Tokens from `text`.
    """
    for match in PAT_ALPHABETIC.finditer(text):
        yield match.group()


def deaccent(text):
    """Remove accentuation from the given string.
    Parameters
    ----------
    text : str
        Input string.
    Returns
    -------
    str
        Unicode string without accentuation.
    Examples
    --------
    >>> from app.utils.utils_EN import deaccent
    >>> deaccent("Šéf chomutovských komunistů dostal poštou bílý prášek")
    u'Sef chomutovskych komunistu dostal postou bily prasek'
    """
    if not isinstance(text, str):
        # assume utf8 for byte strings, use default (strict) error handling
        text = text.decode('utf8')
    norm = unicodedata.normalize("NFD", text)
    result = "".join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize("NFC", result)


def replace_with_separator(text, separator, regexs):
    """Get text with replaced separator if provided regular expressions were matched.
       Parameters
       ----------
       text : str
           Input text.
       separator : str
           The separator between words to be replaced.
       regexs : list of `_sre.SRE_Pattern`
           Regular expressions used in processing text.
       Returns
       -------
       str
           Text with replaced separators.
       """
    # r"\1" is the first match part, and r"\2" is the second match part
    # this function replace the match part between 1 and 2 to a separator
    replacement = r"\1" + separator + r"\2"
    result = text
    for regex in regexs:
        result = regex.sub(replacement, result)
    return result


# def split_sentences(text):
#     # removed the the below cases in order to remove . correctly
#     # so we need remove and undo
#     """Split and get list of sentences from given text. It preserves abbreviations set in
#     :const:`~gensim.summarization.textcleaner.AB_SENIOR` and :const:`~gensim.summarization.textcleaner.AB_ACRONYM`.
#     Parameters
#     ----------
#     text : str
#         Input text.
#     Returns
#     -------
#     list of str
#         Sentences of given text.
#     Example
#     -------
#     >>> from app.utils.utils_EN import split_sentences
#     >>> text = '''Beautiful is better than ugly.
#     ... Explicit is better than implicit. Simple is better than complex.'''
#     >>> split_sentences(text)
#     ['Beautiful is better than ugly.',
#     'Explicit is better than implicit.',
#     'Simple is better than complex.']
#     """
#     processed = _replace_abbreviations(text)
#     return [_undo_replacement(sentence) for sentence in _get_sentences(processed)]


# def _replace_abbreviations(text):
#     # """Replace blank space to '@' separator after abbreviation and next word.
#     # Parameters
#     # ----------
#     # text : str
#     #     Input sentence.
#     # Returns
#     # -------
#     # str
#     #     Sentence with changed separator.
#     # Example
#     # -------
#     # >>> _replace_abbreviations("God bless you, please, Mrs. Robinson")
#     # God bless you, please, Mrs.@Robinson
#     # >>> _replace_abbreviations("God bless you, please, P.S. Robinson")
#     # God bless you, please, P.S.@Robinson
#     # """
#     return replace_with_separator(text, SEPARATOR, [AB_SENIOR, AB_ACRONYM])


# def _undo_replacement(sentence):
#     """Replace `@` separator back to blank space after each abbreviation.
#     Parameters
#     ----------
#     sentence : str
#         Input sentence.
#     Returns
#     -------
#     str
#         Sentence with changed separator.
#     Example
#     -------
#     >>> _undo_replacement("God bless you, please, Mrs.@Robinson")
#     God bless you, please, Mrs. Robinson
#     """
#     return replace_with_separator(sentence, r" ", [UNDO_AB_SENIOR, UNDO_AB_ACRONYM])


# def _get_sentences(text):
#     """
#     Sentence generator from provided text. Sentence pattern set
#        in :const:`~gensim.summarization.textcleaner.RE_SENTENCE`.
#        Parameters
#        ----------
#        text : str
#            Input text.
#        language : str
#             Input language.
#        Yields
#        ------
#        str
#            Single sentence extracted from text.
#        Example
#        -------
#        >>> text = "Does this text contains two sentences? Yes, it does."
#        >>> for sentence in _get_sentences(text):
#        >>>     print(sentence)
#        Does this text contains two sentences?
#        Yes, it does.
#     """
#     for match in RE_SENTENCE_EN.finditer(text):
#         yield match.group()