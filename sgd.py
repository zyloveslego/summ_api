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


if __name__ == '__main__':
    train = pd.read_csv("train_v2_drcat_02.csv")
    # train = train1.sample(100)

    train1 = train[train["label"] == 1].sample(8050)
    print(train1.label.value_counts())
    train = train[train.RDizzl3_seven == True].reset_index(drop=True)
    print(train.label.value_counts())
    train = pd.concat([train, train1])
    train['text'] = train['text'].str.replace('\n', '')
    print(train.label.value_counts())
    correct_df(train)


    def my_tokenizer(x):
        return re.findall(r'[^\W]+', x)


    vectorizer1 = TfidfVectorizer(sublinear_tf=True,
                                  ngram_range=(3, 4),
                                  tokenizer=my_tokenizer,
                                  token_pattern=None,
                                  strip_accents='unicode')

    vectorizer1.fit(train.text)
    X1 = vectorizer1.transform(train.text)

    print("11111")

    vectorizer2 = TfidfVectorizer(sublinear_tf=True,
                                  ngram_range=(3, 6),
                                  tokenizer=my_tokenizer,
                                  token_pattern=None,
                                  strip_accents='unicode')
    vectorizer2.fit(train.text)
    X2 = vectorizer2.transform(train.text)

    print("22222")

    vectorizer3 = TfidfVectorizer(sublinear_tf=True,
                                  ngram_range=(2, 5),
                                  tokenizer=my_tokenizer,
                                  token_pattern=None,
                                  strip_accents='unicode')
    vectorizer3.fit(train.text)
    X3 = vectorizer3.transform(train.text)

    print("33333")

    sgd_model1 = SGDClassifier(max_iter=5000, tol=1e-3, loss="modified_huber")
    sgd_model1.fit(X1, train.label)

    print("44444")

    sgd_model2 = SGDClassifier(max_iter=5000, tol=1e-3, loss="modified_huber", class_weight="balanced")
    sgd_model2.fit(X2, train.label)

    print("55555")

    sgd_model3 = SGDClassifier(max_iter=10000, tol=5e-4, loss="modified_huber", early_stopping=True)
    sgd_model3.fit(X3, train.label)

    print("66666")

    dump(vectorizer1, 'detectai/SGD_model/vectorizer1.pkl', compress=True)
    dump(vectorizer2, 'detectai/SGD_model/vectorizer2.pkl', compress=True)
    dump(vectorizer3, 'detectai/SGD_model/vectorizer3.pkl', compress=True)

    dump(sgd_model1, 'detectai/SGD_model/sgd_classifier_model_1.joblib')
    dump(sgd_model2, 'detectai/SGD_model/sgd_classifier_model_2.joblib')
    dump(sgd_model3, 'detectai/SGD_model/sgd_classifier_model_3.joblib')