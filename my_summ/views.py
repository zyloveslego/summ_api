import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# import os
# import sys
# # __file__ return absolute path in Python3.4, but not in Python 3.5
# sys.path.append(os.path.dirname(__file__) + '/summarization/')
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/summarization/')
from summarization.app.summ.model.kw_summarizer import KWSummarizer
from summarization.app.keywords.keyword import KeyWord
from summarization.app.keywords.keysentence import KeySentence
from summarization.app.summ.model.ks_summarizer import sentence_rank

from nltk.tokenize import sent_tokenize
import jieba
import re


def preprocess(text):
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace(',', ', ')
    text = text.replace('，', ', ')
    text = re.sub(r'\s+', ' ', text)
    return text

def chinese_sentence_segmentation(text):
    seg_list = jieba.cut(text, cut_all=False)
    seg_list = list(seg_list)
    sentences = []
    sentence = ''
    for word in seg_list:
        sentence += word
        if word in ['。', '！', '？', '；', '?', '!', ';']:
            sentences.append(sentence.strip())
            sentence = ''
    if sentence:
        sentences.append(sentence.strip())
    return sentences


def get_sentences_rank(text, ratio=1, algorithm='', article_structure=1, lang='en'):
    if lang == 'zh-cn' or lang == 'zh-tw':
        language = 'chinese'
        summarizer_name = 'TW'
    else:
        language = 'english'
        summarizer_name = 'TW'

    customized_textrank = KeyWord.basic_init(language=language, weighting_method="CO_OCCUR")  # CO_OCCUR_W2V
    summarizer = KWSummarizer.factory(language=language, summarizer_name=summarizer_name,
                                      customized_textrank=customized_textrank)

    # sentence_list = text_util.segment_by_sentence(text, lang)
    # summarize() doesn't support text as list type

    if isinstance(text, list):
        if len(text) >= 1700:
            print("long text")
            sentence_score_list = summarizer.summarize_combine_sentence(text, sentence_ratio=1, show_ranking=True,
                                                                        show_score=True)
        else:
            print("short text")
            sentence_score_list = summarizer.summarize(text, sentence_ratio=1, show_ranking=True, show_score=True)

    else:
        if language == 'chinese':
            temp_list = chinese_sentence_segmentation(text)
        else:
            temp_list = sent_tokenize(text)

        if len(temp_list) >= 1700:
            print("long text")
            sentence_score_list = summarizer.summarize_combine_sentence(text, sentence_ratio=1, show_ranking=True,
                                                                        show_score=True)
        else:
            print("short text")
            sentence_score_list = summarizer.summarize(text, sentence_ratio=1, show_ranking=True, show_score=True)

    return sentence_score_list


# def get_sentences_rank_from_dict(text, ratio=1, algorithm='', article_structure=1, lang='en'):
#     if lang == 'zh-cn' or lang == 'zh-tw':
#         language = 'chinese'
#         summarizer_name = 'TW'
#     else:
#         language = 'english'
#         summarizer_name = 'TW'
#
#     customized_textrank = KeyWord.basic_init(language=language, weighting_method="CO_OCCUR")  # CO_OCCUR_W2V
#     summarizer = KWSummarizer.factory(language=language, summarizer_name=summarizer_name,
#                                       customized_textrank=customized_textrank)
#
#     # sentence_list = text_util.segment_by_sentence(text, lang)
#     # summarize() doesn't support text as list type
#     sentence_score_list = summarizer.summarize(text, sentence_ratio=1, show_ranking=True, show_score=True)
#
#     return sentence_score_list


@csrf_exempt
def sentence_rank(request):
    text = ""
    if request.method == 'POST':
        text = request.POST.get('text')

    if request.method == 'GET':
        return JsonResponse({})

    # print(request.POST)
    # print(text)
    # text = open("/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/summarization/tests/summ_test/test_data/swr.txt").read()

    from langdetect import detect

    lang = detect(text)
    print(lang)
    if lang == 'zh-cn' or lang == 'zh-tw':
        text = preprocess(text)

    ranked_sentence = get_sentences_rank(text, lang=lang)
    ranked_sentence.sort(key=lambda x: x[2], reverse=True)
    data = {
        'sentence_rank': ranked_sentence
    }

    return JsonResponse(data)


@csrf_exempt
def sentence_rank_from_dict(request):
    text_dict = None
    if request.method == 'POST':
        # print(request.POST)
        text_dict = request.POST.get('text')

    if request.method == 'GET':
        return JsonResponse({})

    key_list = []
    ori_text_list = []
    text_list = []

    get_dict = json.loads(text_dict)

    from langdetect import detect

    lang = detect(''.join(get_dict.values()))
    print(lang)

    for key, value in get_dict.items():
        key_list.append(key)
        if lang == 'zh-cn' or lang == 'zh-tw':
            text_list.append(preprocess(value))
            ori_text_list.append(value)
        else:
            text_list.append(value)
            ori_text_list.append(value)

    # print(text_list)

    ranked_sentence = get_sentences_rank(text_list, lang=lang)
    # print(ranked_sentence)
    ranked_sentence.sort(key=lambda x: x[2], reverse=True)

    return_dict = []

    for i in ranked_sentence:
        # print(i)
        i = list(i)
        # i[0] = key_list[text_list.index(i[1])]
        return_dict.append([key_list[text_list.index(i[1])], ori_text_list[text_list.index(i[1])], i[2], i[3]])

    data = {
        'sentence_rank': return_dict
    }

    return JsonResponse(data)


@csrf_exempt
def sentence_rank_from_dict_zh(request):
    text_dict = None
    if request.method == 'POST':
        # print(request.POST)
        text_dict = request.POST.get('text')

    if request.method == 'GET':
        return JsonResponse({})

    key_list = []
    text_list = []

    get_dict = json.loads(text_dict)

    for key, value in get_dict.items():
        key_list.append(key)
        text_list.append(value)

    # print(text_list)

    ranked_sentence = get_sentences_rank(text_list, lang='zh')
    ranked_sentence.sort(key=lambda x: x[2], reverse=True)

    return_dict = []

    for i in ranked_sentence:
        i = list(i)
        # i[0] = key_list[text_list.index(i[1])]
        return_dict.append([key_list[text_list.index(i[1])], i[1], i[2], i[3]])

    data = {
        'sentence_rank': return_dict
    }

    return JsonResponse(data)


@csrf_exempt
def sentence_rank_ks(request):
    text_dict = None
    if request.method == 'POST':
        # print(request.POST)
        text_dict = request.POST.get('text')

    if request.method == 'GET':
        return JsonResponse({})

    key_list = []
    text_list = []

    get_dict = json.loads(text_dict)

    for key, value in get_dict.items():
        key_list.append(key)
        text_list.append(value)

    # print(get_dict)
    # text_list = """
    # Certain analytical queries, such as “how many active users are on the ‘web’ platform”, may generate SQL queries that do not conform to the database’s actual values if generated naively. For example, the where clause in the response might bewhere platform=’web’ as opposed to the correct where platform=’WEB’. To address such issues, unique values of low-cardinality columns which would frequently be used for this kind of filtering are processed and incorporated into the table schema, so that the LLM can make use of this information to generate precise SQL queries.
    # """

    extractor = KeySentence.basic_init(language="english")
    # sen_extractor = sentence_rank

    generated_sentences = extractor.extract(text_list, ratio=1, return_scores=True, position_topic_biased=1,
                                            article_structure=2)
    generated_sentences.sort(key=lambda x: x[1], reverse=True)

    return_dict = []

    # for i in generated_sentences:
    #     print(i)
    # i = list(i)
    # i[0] = key_list[text_list.index(i[1])]
    # return_dict.append([key_list[text_list.index(i[1])], i[1], i[2], i[3]])

    data = {
        'sentence_rank': return_dict
    }

    return JsonResponse(data)
