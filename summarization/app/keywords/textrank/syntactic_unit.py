class SyntacticUnit(object):
    """SyntacticUnit class.

    Attributes
    ----------
    text : str
        Input text.
    token : str
        Tokenized text.
    tag : str
        Tag of unit, optional.
    index : int
        Index of sytactic unit in corpus, optional.
    score : float
        Score of synctatic unit, optional.

    """

    def __init__(self, text, token=None, tag=None):
        """

        Parameters
        ----------
        text : str
            Input text.
        token : str
            Tokenized text, optional.
        tag : str
            Tag of unit, optional.

        """
        self.text = text
        self.token = token
        self.tag = tag[:2] if tag else None  # Just first two letters of tag
        self.index = -1
        self.score = -1

    def __str__(self):
        return "Original unit: '" + self.text + "' *-*-*-* " + "Processed unit: '" + self.token + "'"

    def __repr__(self):
        return str(self)

    @staticmethod
    def merge_syntactic_units(original_units, filtered_units=None, tags=None):
        units = []

        for i in range(len(original_units)):
            if filtered_units:
                # if filtered_unit exist, then filter it
                if filtered_units[i] == '':
                    continue

                text = original_units[i]
                token = filtered_units[i]
                tag = tags[i][1] if tags is not None and i < len(tags) else None
                unit = SyntacticUnit(text, token, tag)
                unit.index = i

                units.append(unit)
            else:
                # if filtered_unit not exist, add the original word only.
                text = original_units[i]
                tag = tags[i][1] if tags is not None and i < len(tags) else None
                unit = SyntacticUnit(text, tag=tag)
                unit.index = i

                units.append(unit)

        return units

    @staticmethod
    def to_dict(syntactic_list):
        return {unit.text: unit for unit in syntactic_list}

    @staticmethod
    def to_text_list(syntactic_list):
        return [unit.text for unit in syntactic_list]
