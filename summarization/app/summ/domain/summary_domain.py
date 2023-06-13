class SummaryData(object):

    def __init__(self):
        self._doc_no = ""
        self._headline = ""
        self._text = ""
        self._text_list = []
        self._gold_standard_limitation_method = None
        self._gold_standard_limitation_para = None
        self._gold_standard = {}
        self._generated_summary = []
        self._rouge_1_score = 0
        self._rouge_2_score = 0
        self._rouge_l_score = 0

    @property
    def doc_no(self):
        return self._doc_no

    @doc_no.setter
    def doc_no(self, doc_no):
        self._doc_no = doc_no

    @property
    def gold_standard_limitation_method(self):
        return self._gold_standard_limitation_method

    @gold_standard_limitation_method.setter
    def gold_standard_limitation_method(self, gold_standard_limitation_method):
        self._gold_standard_limitation_method = gold_standard_limitation_method

    @property
    def gold_standard_limitation_para(self):
        return self._gold_standard_limitation_para

    @gold_standard_limitation_para.setter
    def gold_standard_limitation_para(self, gold_standard_limitation_para):
        self._gold_standard_limitation_para = gold_standard_limitation_para

    @property
    def headline(self):
        return self._headline

    @headline.setter
    def headline(self, headline):
        self._headline = headline

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def text_list(self):
        return self._text_list

    @text_list.setter
    def text_list(self, text_list):
        # test input is in format [string list]
        if text_list and type(text_list) == list and all(isinstance(s, str) for s in text_list):
            self._text_list = text_list
        else:
            raise Exception(self.doc_no + " having trouble setting text")

    @property
    def gold_standard(self):
        return self._gold_standard

    @gold_standard.setter
    def gold_standard(self, gold_standard_dict):
        # test input is in format [[string list], [string list]]
        if gold_standard_dict and type(gold_standard_dict) == dict\
                and all(sentence_list and type(sentence_list) == list
                        for judge_id, sentence_list in gold_standard_dict.item()) \
                and all(isinstance(s, str)
                        for judge_id, sentence_list in gold_standard_dict.item() for s in sentence_list):
            self._gold_standard = gold_standard_dict
        else:
            raise Exception(self.doc_no + " having trouble setting gold_standard_list")

    @property
    def generated_summary(self):
        return self._generated_summary

    @generated_summary.setter
    def generated_summary(self, generated_summary):
        # test input is in format [string list]
        if generated_summary and type(generated_summary) == list and all(isinstance(s, str) for s in generated_summary):
            self._generated_summary = generated_summary
        else:
            raise Exception(self.doc_no + " having trouble setting generate_summary")

    @property
    def rouge_1_score(self):
        return self._rouge_1_score

    @rouge_1_score.setter
    def rouge_1_score(self, rouge_1_score):
        self._rouge_1_score = rouge_1_score

    @property
    def rouge_2_score(self):
        return self._rouge_2_score

    @rouge_2_score.setter
    def rouge_2_score(self, rouge_2_score):
        self._rouge_2_score = rouge_2_score

    @property
    def rouge_l_score(self):
        return self._rouge_l_score

    @rouge_l_score.setter
    def rouge_l_score(self, rouge_l_score):
        self._rouge_l_score = rouge_l_score

    def append_gold_standard(self, judge_id, sentence_list):
        if sentence_list and type(sentence_list) == list and all(isinstance(s, str) for s in sentence_list):
            if judge_id in self.gold_standard:
                raise Exception("Duplicate judge for a single doc")
            self.gold_standard[judge_id] = sentence_list
        else:
            raise Exception(self.doc_no + "having trouble append a gold stand")

    def get_references(self):
        # [ref1, ref2]
        references = []
        for judge_id, sentence_list in self._gold_standard.items():
            references.append(" ".join(sentence_list))
        return references

    def get_references_sentence_list(self):
        # [ref[s1, s2, s3], ref2[s1, s2, s3]]
        references = []
        for judge_id, sentence_list in self._gold_standard.items():
            references.append(sentence_list)
        return references

    def get_generated_summary(self):
        return " ".join(self._generated_summary)
