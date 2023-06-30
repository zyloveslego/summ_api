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


def get_sentences_rank(text, ratio=1, algorithm='', article_structure=3, lang='en'):
    if lang == 'zh':
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
    sentence_score_list = summarizer.summarize(text, sentence_ratio=1, show_ranking=True, show_score=True,
                                               article_structure=article_structure)

    return sentence_score_list


def get_sentences_rank_from_dict(text, ratio=1, algorithm='', article_structure=3, lang='en'):
    if lang == 'zh':
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
    sentence_score_list = summarizer.summarize(text, sentence_ratio=1, show_ranking=True, show_score=True,
                                               article_structure=article_structure)

    return sentence_score_list


@csrf_exempt
def sentence_rank(request):
    text = ""
    if request.method == 'POST':
        text = request.POST.get('text')

    if request.method == 'GET':
        return JsonResponse({})

    # print(text)
    # text = open("/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/summarization/tests/summ_test/test_data/swr.txt").read()
    sentence_rank = get_sentences_rank(text)
    sentence_rank.sort(key=lambda x: x[2], reverse=True)
    data = {
        'sentence_rank': sentence_rank
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

    # print(text)
    text_list = []
    for key, value in json.loads(text_dict).items():
        text_list.append(value)

    # print(text_list)

    sentence_rank = get_sentences_rank(text_list)
    sentence_rank.sort(key=lambda x: x[2], reverse=True)
    data = {
        'sentence_rank': sentence_rank
    }

    return JsonResponse(data)
