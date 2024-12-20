from django.shortcuts import render
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import copy
import tiktoken
from langdetect import detect
from rest_framework.decorators import api_view

import openai
import argparse
from nltk.stem.porter import PorterStemmer
import re, six
from rouge_score.rouge_scorer import _create_ngrams

import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
import tqdm
import json
import os
import torch
import random, time
from openai import OpenAI

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import SGDClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, accuracy_score

from concurrent.futures import ProcessPoolExecutor
import re
from joblib import dump, load

import language_tool_python


def my_tokenizer(x):
    return re.findall(r'[^\W]+', x)

cur_path = os.getcwd() + "/detectai"

# vectorizer1 = load(cur_path + '/SGD_model/vectorizer1.pkl')
# vectorizer2 = load(cur_path + '/SGD_model/vectorizer2.pkl')
# vectorizer3 = load(cur_path + '/SGD_model/vectorizer3.pkl')
#
# sgd_model1 = load(cur_path + '/SGD_model/sgd_classifier_model_1.joblib')
# sgd_model2 = load(cur_path + '/SGD_model/sgd_classifier_model_2.joblib')
# sgd_model3 = load(cur_path + '/SGD_model/sgd_classifier_model_3.joblib')

vectorizer1 = None
vectorizer2 = None
vectorizer3 = None

sgd_model1 = None
sgd_model2 = None
sgd_model3 = None


import language_tool_python

tool = language_tool_python.LanguageTool('en-US')


# 修正数据
def denoise_text(text):
    # Assuming 'tool' is defined elsewhere in your code
    corrected_text = tool.correct(text)
    return corrected_text


# Function to correct the 'text' column of a DataFrame or Series in parallel
def correct_df(input_data):
    if isinstance(input_data, pd.DataFrame):
        # If input is a DataFrame, correct the 'text' column
        with ProcessPoolExecutor() as executor:
            input_data['text'] = list(executor.map(denoise_text, input_data['text']))
    elif isinstance(input_data, pd.Series):
        # If input is a Series, correct the series
        with ProcessPoolExecutor() as executor:
            input_data = list(executor.map(denoise_text, input_data))

# cur_path = os.getcwd() + "/detectai/"
# train = pd.read_csv(cur_path + "SGD_model/train_v2_drcat_02.csv")
# # train = train1.sample(100)
#
# train1 = train[train["label"] == 1].sample(8050)
# print(train1.label.value_counts())
# train = train[train.RDizzl3_seven == True].reset_index(drop=True)
# print(train.label.value_counts())
# train = pd.concat([train, train1])
# train['text'] = train['text'].str.replace('\n', '')
# print(train.label.value_counts())
# correct_df(train)
#
#
# def my_tokenizer(x):
#     return re.findall(r'[^\W]+', x)
#
#
# vectorizer1 = TfidfVectorizer(sublinear_tf=True,
#                               ngram_range=(3, 4),
#                               tokenizer=my_tokenizer,
#                               token_pattern=None,
#                               strip_accents='unicode')
#
# vectorizer1.fit(train.text)
# X1 = vectorizer1.transform(train.text)
#
# vectorizer2 = TfidfVectorizer(sublinear_tf=True,
#                               ngram_range=(3, 6),
#                               tokenizer=my_tokenizer,
#                               token_pattern=None,
#                               strip_accents='unicode')
# vectorizer2.fit(train.text)
# X2 = vectorizer2.transform(train.text)
#
# vectorizer3 = TfidfVectorizer(sublinear_tf=True,
#                               ngram_range=(2, 5),
#                               tokenizer=my_tokenizer,
#                               token_pattern=None,
#                               strip_accents='unicode')
# vectorizer3.fit(train.text)
# X3 = vectorizer3.transform(train.text)
#
# sgd_model1 = SGDClassifier(max_iter=5000, tol=1e-3, loss="modified_huber")
# sgd_model1.fit(X1, train.label)
#
# sgd_model2 = SGDClassifier(max_iter=5000, tol=1e-3, loss="modified_huber", class_weight="balanced")
# sgd_model2.fit(X2, train.label)
#
# sgd_model3 = SGDClassifier(max_iter=10000, tol=5e-4, loss="modified_huber", early_stopping=True)
# sgd_model3.fit(X3, train.label)


# Create your views here.
def front(request):
    return render(request, 'detectai/frontpage.html')


@csrf_exempt
@api_view(['POST'])
def SGDClassifier(request):
    text = request.data.get("text")

    text = denoise_text(text)

    test1 = vectorizer1.transform([text])
    test2 = vectorizer2.transform([text])
    test3 = vectorizer3.transform([text])

    preds_test1 = sgd_model1.predict_proba(test1)[:, 1]
    preds_test2 = sgd_model2.predict_proba(test2)[:, 1]
    preds_test3 = sgd_model3.predict_proba(test3)[:, 1]

    preds_test = np.average([preds_test1, preds_test2, preds_test3], axis=0, weights=[0.6, 0.2, 0.2])[0]

    if preds_test > 0.5:
        humanorai = "AI"
    else:
        humanorai = "Human"

    response_data = {'Human or AI': humanorai, 'percent': preds_test}

    return JsonResponse(response_data)

@csrf_exempt
@api_view(['POST'])
def loglikely(request):
    text = request.data.get("text")

    print(text)

    def get_davinci003_response(prompt: str, max_tokens=150, temperature=0.7, top_p=1, n=1, logprobs=1, stop=None,
                                echo=True):
        client = OpenAI(api_key="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")
        response = client.completions.create(model="text-davinci-003",
                                             prompt=prompt,
                                             max_tokens=max_tokens,
                                             temperature=temperature,
                                             top_p=top_p,
                                             n=n,
                                             logprobs=logprobs,
                                             stop=stop,
                                             echo=echo)
        # output = response['choices'][0]['text']
        # assert output.startswith(prompt)
        # gen_text = output[len(prompt):].strip()
        return response

    max_new_tokens = 300
    truncate_ratio = 0.7
    regen_number = 20

    # input_text = "LLMs can reason about wide-ranging topics, but their knowledge is limited to the public data up to a specific point in time that they were trained on. If you want to build AI applications that can reason about private data or data introduced after a model's cutoff date, you need to augment the knowledge of the model with the specific information it needs. The process of bringing the appropriate information and inserting it into the model prompt is known as Retrieval Augmented Generation (RAG)."

    prefix = "Continues the passage from the sentences provided in 180-300 words."

    prefix_input_text = prefix + '\n' + text[:int(truncate_ratio * len(text))]

    generate_half = get_davinci003_response(prompt=prefix_input_text,
                                            max_tokens=max_new_tokens,
                                            n=regen_number,
                                            logprobs=5,
                                            echo=False)

    original_response = get_davinci003_response(prompt=text,
                                                max_tokens=0,
                                                n=1,
                                                logprobs=5,
                                                echo=True)

    original_response_truncate = get_davinci003_response(prompt=prefix_input_text,
                                                         max_tokens=0,
                                                         n=1,
                                                         logprobs=5,
                                                         echo=True)

    truncate_len = len(original_response_truncate.choices[0].logprobs.token_logprobs)
    orignal_prob = original_response.choices[0].logprobs.token_logprobs[truncate_len:]
    orignal_logprob = np.mean(orignal_prob)

    num_samples = 20
    regen_probs = [sum(generate_half.choices[0].logprobs.token_logprobs) / \
                   len(generate_half.choices[0].logprobs.token_logprobs) for i in range(num_samples) \
                   if len(generate_half.choices[0].logprobs.token_logprobs) != 0]
    regen_logprobs_avg_20 = np.mean(regen_probs)
    # print(regen_logprobs_avg_20)
    original_th = orignal_logprob - regen_logprobs_avg_20
    # print(original_th)

    threshold = -0.6737804433843368

    score = original_th

    if str(score) == 'nan':
        response_data = {'humanorai': "Human", 'percent': "Nan"}

        return JsonResponse(response_data)


    if score < threshold:
        # human write
        # 0 - threshold
        percent = abs(((threshold - score) / threshold) * 0.5) + 0.5
        if percent > 1:
            percent = 1
        humanorai = "Human"
        # print("human write")
        # print("{:.3f}".format(percent))
    else:
        # machine write
        # threshold - ? (暂定0.01)
        percent = abs(((score - threshold) / (0.0 - threshold)) * 0.5) + 0.5
        if percent > 1:
            percent = 1
        humanorai = "AI"
        # print("machine write")
        # print("{:.3f}".format(percent))

    response_data = {'Human or AI': humanorai, 'percent': percent}

    return JsonResponse(response_data)


@csrf_exempt
@api_view(['POST'])
def overlapwithwords(request):
    text = request.data.get("text")

    print(text)

    client = OpenAI(api_key="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")

    model = "gpt-3.5-turbo"
    max_new_tokens = 300
    regen_number = 10
    truncate_ratio = 0.5
    temperature = 0.7

    def tokenize(text, stemmer, stopwords=[]):
        """Tokenize input text into a list of tokens.

        This approach aims to replicate the approach taken by Chin-Yew Lin in
        the original ROUGE implementation.

        Args:
        text: A text blob to tokenize.
        stemmer: An optional stemmer.

        Returns:
        A list of string tokens extracted from input text.
        """

        # Convert everything to lowercase.
        text = text.lower()
        # Replace any non-alpha-numeric characters with spaces.
        text = re.sub(r"[^a-z0-9]+", " ", six.ensure_str(text))

        tokens = re.split(r"\s+", text)
        if stemmer:
            # Only stem words more than 3 characters long.
            tokens = [stemmer.stem(x) if len(x) > 3 else x for x in tokens if x not in stopwords]

        # One final check to drop any empty or invalid tokens.
        tokens = [x for x in tokens if re.match(r"^[a-z0-9]+$", six.ensure_str(x))]

        return tokens

    def get_score_ngrams(target_ngrams, prediction_ngrams):
        intersection_ngrams_count = 0
        ngram_dict = {}
        for ngram in six.iterkeys(target_ngrams):
            intersection_ngrams_count += min(target_ngrams[ngram],
                                             prediction_ngrams[ngram])
            ngram_dict[ngram] = min(target_ngrams[ngram], prediction_ngrams[ngram])
        target_ngrams_count = sum(target_ngrams.values())  # prediction_ngrams
        return intersection_ngrams_count / max(target_ngrams_count, 1), ngram_dict

    def get_ngram_info(article_tokens, summary_tokens, _ngram):
        # _create_ngrams return a counter
        article_ngram = _create_ngrams(article_tokens, _ngram)
        summary_ngram = _create_ngrams(summary_tokens, _ngram)
        ngram_score, ngram_dict = get_score_ngrams(article_ngram, summary_ngram)
        return ngram_score, ngram_dict, sum(ngram_dict.values())

    def N_gram_detector(ngram_n_ratio):
        score = 0
        non_zero = []

        for idx, key in enumerate(ngram_n_ratio):
            if idx in range(3) and 'score' in key or 'ratio' in key:
                score += 0. * ngram_n_ratio[key]
                continue
            if 'score' in key or 'ratio' in key:
                score += (idx + 1) * np.log((idx + 1)) * ngram_n_ratio[key]
                if ngram_n_ratio[key] != 0:
                    non_zero.append(idx + 1)
        return score / (sum(non_zero) + 1e-8)

    # input_text = "LLMs can reason about wide-ranging topics, but their knowledge is limited to the public data up to a specific point in time that they were trained on. If you want to build AI applications that can reason about private data or data introduced after a model's cutoff date, you need to augment the knowledge of the model with the specific information it needs. The process of bringing the appropriate information and inserting it into the model prompt is known as Retrieval Augmented Generation (RAG)."

    get_half = text[:int(truncate_ratio * len(text))]
    gpt_gen_half = client.chat.completions.create(model=model,
                                                  messages=[{"role": "system",
                                                             "content": "You are a helpful assistant that continues the passage from the sentences provided."},
                                                            #  {"role": "user", "content": dd['question']}, # mask out to simulate no golden prompt
                                                            {"role": "user", "content": get_half},
                                                            ],
                                                  temperature=temperature,
                                                  max_tokens=max_new_tokens,
                                                  n=regen_number)

    get_rest_half = text[int(truncate_ratio * len(text)):]

    ori_rest_half_tokens = tokenize(get_rest_half, stemmer=PorterStemmer())

    gpt_gen_half = gpt_gen_half.choices

    temp2 = {}
    for i in range(10):  # len(human_half)
        gpt_gen_tokens = tokenize(gpt_gen_half[i].message.content, stemmer=PorterStemmer())
        if len(gpt_gen_tokens) == 0:
            continue

        for _ngram in range(1, 25):
            ngram_score, ngram_dict, overlap_count = get_ngram_info(ori_rest_half_tokens, gpt_gen_tokens, _ngram)
            temp2['gpt_truncate_ngram_{}_score'.format(_ngram)] = ngram_score / len(gpt_gen_tokens)
            temp2['gpt_truncate_ngram_{}_count'.format(_ngram)] = overlap_count

    score = N_gram_detector(temp2)

    threshold = 0.0018777647266036849

    if score < threshold:
        # human write
        # 0 - threshold
        percent = ((threshold - score) / threshold) * 0.5 + 0.5
        if percent > 1:
            percent = 1
        humanorai = "Human"
        # print("human write")
        # print("{:.3f}".format(percent))
    else:
        # machine write
        # threshold - ? (暂定0.01)
        percent = ((score - threshold) / (0.01 - threshold)) * 0.5 + 0.5
        if percent > 1:
            percent = 1
        humanorai = "AI"
        # print("machine write")
        # print("{:.3f}".format(percent))

    response_data = {'Human or AI': humanorai, 'percent': percent}

    return JsonResponse(response_data)


@csrf_exempt
@api_view(['POST'])
def gpt_finetune(request):
    text = request.data.get("text")

    from openai import OpenAI
    client = OpenAI(api_key="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")

    system_prompt = "Tell me whether the following text is written by human or AI."

    # test_text = """
    # Let's put it all together into a chain that takes a question, retrieves relevant documents, constructs a prompt, passes that to a model, and parses the output.
    # """

    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0613:librum2::8S6gl6nA",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    # print(response)

    if "AI" in response.choices[0].message.content:
        humanorai = "AI"
    else:
        humanorai = "Human"

    response_data = {'Human or AI': humanorai, 'percent': None}

    return JsonResponse(response_data)
