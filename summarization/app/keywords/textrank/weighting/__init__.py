from summarization.app.keywords.textrank.weighting.co_occurrence import CoOccur
from summarization.app.keywords.textrank.weighting.edit_dist import EditDist
from summarization.app.keywords.textrank.weighting.w2v import W2V
from summarization.app.keywords.textrank.weighting.co_occurr_w2v import CoOccur_W2V
from summarization.app.keywords.textrank.weighting.pmi import PMI
from summarization.app.keywords.textrank.weighting.pmi_w2v import PMI_W2V
from summarization.app.keywords.textrank.weighting.sen_co_occurrence import SentenceCoOccur


def factory(language, weighting_method, word_or_sentence):
    """
    A Factory function for DUC Parser, DUC contains many kind of format.
    So each format need a specific parser.
    :param weighting_method: weighting_method Name
    :return: A weighting method
    """
    if word_or_sentence == "WORD":
        # parser_name = ap means this parse all the articles doc name starts with AP
        if weighting_method == "CO_OCCUR":
            return CoOccur(language)
        if weighting_method == "EDIT_DIST":
            return EditDist()
        if weighting_method == "W2V":
            return W2V(language)
        if weighting_method == "CO_OCCUR_W2V":
            return CoOccur_W2V(language)
        if weighting_method == "PMI":
            return PMI(language)
        if weighting_method == "PMI_W2V":
            return PMI_W2V(language)
        else:
            # Parser for other format hasn't been writen yet
            assert 0, "bad weighting method request: " + word_or_sentence + " " + weighting_method
    if word_or_sentence == "SENTENCE":
        # parser_name = ap means this parse all the articles doc name starts with AP
        if weighting_method == "CO_OCCUR":
            return SentenceCoOccur(language)
        if weighting_method == "CO_OCCUR_WMD":
            return CoOccur_W2V(language)
        else:
            # Parser for other format hasn't been writen yet
            assert 0, "bad weighting method request: " + word_or_sentence + " " + weighting_method

