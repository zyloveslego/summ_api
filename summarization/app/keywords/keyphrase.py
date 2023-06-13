# class KeyWord(object):
#     """
#     KeyWord Extraction
#     Base Method:
#         :TEXTRANK The Original textrank method.
#
#     Candidate Method:
#         :Word Use word Only
#
#     Scoring:
#         :EDD Edit distance
#         :CO Co-occurrence
#         :WMD/W2V Use Word2vec or WMD base on Candidate method
#     """
#
#     @staticmethod
#     def factory(extractor_name):
#         # parser_name = ap means this parse all the articles doc name starts with AP
#         if extractor_name == "AP":
#             return APDUCParser()
#         else:
#             # Parser for other format hasn't been writen yet
#             assert 0, "bad request: " + extractor_name
