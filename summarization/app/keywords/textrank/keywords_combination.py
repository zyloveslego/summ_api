from app.keywords.textrank.syntactic_unit import SyntacticUnit


class Combinator(object):
    def __init__(self, language, max_combine_length=None, remove=True, allow_duplication=False):
        """
        :return:
        :param language:
        :param remove: if true, combinator will run the basic combination
                and then remove the combination length > max_combine_length
                if false, combine_allow_duplication will work
        :param max_combine_length: combination length, to prevent keywords too long.
        :param allow_duplication: allow duplication will allow keywords appear in several combination.
                ex. allow I like you very much. => I like, like you, you very, very much. length = 2
                ex. not allow I like you very much. => I like, you very, much. length = 2
        """
        self.language = language
        self.remove = remove
        # combination settings see setter for detail
        self.max_combine_length = max_combine_length
        self.allow_duplication = allow_duplication

    def _split_text(self, text, original_tokens):
        if self.language == "chinese":
            # chinese need to use the original tokens,
            return original_tokens
        else:
            # english need to split cause english is already space separated.
            # do not use original tokens, original tokens does not contain punctuation, will result in mistakes
            # ex. I like you, me too. "you me" can be a combined keywords.
            return text.split()

    def combine_keywords(self, _keywords, text, original_tokens, tokenizer):
        split_text = self._split_text(text, original_tokens)

        if self.allow_duplication:
            # remove the combined keywords with allow duplication see the function for detail
            return self._get_combined_keywords_with_len_and_dup(_keywords, split_text, tokenizer)

        # if max_combine_length is None, means use the basic method with no remove, and no combine_allow_duplication
        if self.max_combine_length is None or self.max_combine_length <= 0:
            return self._get_combined_keywords(_keywords, split_text, tokenizer)

        # just remove the combined keywords that exceed the limit
        if self.max_combine_length:
            combined_keywords = self._get_combined_keywords(_keywords, split_text, tokenizer)
            if self.remove:
                return self._remove_exceed_limit(combined_keywords)
            else:
                return combined_keywords

        return [key for key in _keywords]

    def _remove_exceed_limit(self, combined_keywords):
        removed_list = []
        for combined_keyword in combined_keywords:
            if len(combined_keyword.split()) <= self.max_combine_length:
                removed_list.append(combined_keyword)
        return removed_list

    def _get_combined_keywords(self, _keywords, split_text, tokenizer):
        combined_keywords = []
        _keywords = _keywords.copy()
        len_text = len(split_text)
        for i in range(len_text):
            word = self._strip_word(tokenizer, split_text[i])
            if word in _keywords:
                combined_word = [word]
                if i + 1 == len_text:
                    combined_keywords.append(word)  # appends last word if keyword and doesn't iterate
                for j in range(i + 1, len_text):
                    other_word = self._strip_word(tokenizer, split_text[j])
                    if other_word in _keywords and other_word == split_text[j] \
                            and other_word not in combined_word:
                        combined_word.append(other_word)
                    else:
                        for keyword in combined_word:
                            _keywords.pop(keyword)
                        combined_keywords.append(" ".join(combined_word))
                        break
        return combined_keywords

    def _get_combined_keywords_with_len_and_dup(self, _keywords, split_text, tokenizer):
        combined_keywords = []
        _keywords = _keywords.copy()
        len_text = len(split_text)
        for i in range(len_text):
            word = self._strip_word(tokenizer, split_text[i])
            if word in _keywords:
                combined_word = [word]
                if i + 1 == len_text:
                    combined_keywords.append(word)  # appends last word if keyword and doesn't iterate
                for j in range(i + 1, len_text):
                    other_word = self._strip_word(tokenizer, split_text[j])
                    if other_word in _keywords and other_word == split_text[j] \
                            and other_word not in combined_word:
                        if len(combined_word) <= self.max_combine_length:
                            combined_word.append(other_word)
                        else:
                            if self.allow_duplication:
                                # only pop the first word.
                                # len = 2 and combined_word = [I love you]
                                #   => only "I" removed, so love could still in the list. [love you]
                                _keywords.pop(combined_word[0])
                                combined_keywords.append(" ".join(combined_word))
                                break
                            else:
                                # remove all the word
                                # len = 2 and combined_word = [I love you]
                                #   => "I love" are removed, so only left [ you]
                                for keyword in combined_word:
                                    _keywords.pop(keyword)
                                combined_keywords.append(" ".join(combined_word))
                                break
                    else:
                        for keyword in combined_word:
                            _keywords.pop(keyword)
                        combined_keywords.append(" ".join(combined_word))
                        break
        return combined_keywords

    def _get_combined_keywords_with_len_and_w_duplication(self, _keywords, split_text, tokenizer):
        combined_keywords = []
        _keywords = _keywords.copy()
        len_text = len(split_text)
        for i in range(len_text):
            word = self._strip_word(tokenizer, split_text[i])
            if word in _keywords:
                combined_word = [word]
                if i + 1 == len_text:
                    combined_keywords.append(word)  # appends last word if keyword and doesn't iterate
                for j in range(i + 1, len_text):
                    other_word = self._strip_word(tokenizer, split_text[j])
                    if other_word in _keywords and other_word == split_text[j] \
                            and other_word not in combined_word:
                        if len(combined_word) <= self.max_combine_length:
                            combined_word.append(other_word)
                        else:
                            # only pop the first word.
                            # combined_word = [I love you] => only "I" removed, so love could still in the list.
                            _keywords.pop(combined_word[0])
                            combined_keywords.append(" ".join(combined_word))
                            break
                    else:
                        for keyword in combined_word:
                            _keywords.pop(keyword)
                        combined_keywords.append(" ".join(combined_word))
                        break
        return combined_keywords

    def _strip_word(self, tokenizer, word):
        stripped_word_list = SyntacticUnit.to_text_list(
            tokenizer.tokenize_by_word(word, apply_token_filters=False, apply_tag_filters=False))
        return stripped_word_list[0] if stripped_word_list else ""
