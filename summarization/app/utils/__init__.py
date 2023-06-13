from summarization.app.utils.utils_EN import UtilsEN
from summarization.app.utils.utils_CN import UtilsCN


def factory(language):
    if language == "english":
        return UtilsEN(language)
    elif language == "chinese":
        return UtilsCN(language)
    else:
        # Parser for other format hasn't been writen yet
        assert 0, "bad weighting method request: " + language
