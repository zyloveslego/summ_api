from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.datasets import fetch_20newsgroups
import pickle
from app.keywords.textrank.tokenizer import Tokenizer
import numpy as np


def doc_preprocessing(tokenizer, doc):
    doc = doc.replace("_", " ")
    token_list = tokenizer.tokenize_by_word(doc, apply_token_filters=True)
    tag_filtered_tokens = tokenizer.pos_tag_filter(token_list)
    return " ".join(tag_filtered_tokens)


def lda_training_en(corpus):
    no_features = 10000

    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(corpus)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tf = tf_vectorizer.fit_transform(corpus)
    tf_feature_names = tf_vectorizer.get_feature_names()

    no_topics = 20

    # Run NMF
    nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

    # Run LDA
    lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online', learning_offset=50.,
                                    random_state=0).fit(tf)

    no_top_words = 10
    display_topics(nmf, tfidf_feature_names, no_top_words)
    display_topics(lda, tf_feature_names, no_top_words)

    with open('nmf.pkl', 'wb') as f:
        pickle.dump(nmf, f)

    with open('lda.pkl', 'wb') as f:
        pickle.dump(lda, f)

    with open('tf_vectorizer.pkl', 'wb') as f:
        pickle.dump(tf_vectorizer, f)


def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))


def training():
    tokenizer = Tokenizer.factory("english")
    dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
    documents = dataset.data

    processed_docs = []
    for doc in documents:
        doc = doc.replace("_", " ")
        doc = doc_preprocessing(tokenizer, doc)
        processed_docs.append(doc)

    lda_training_en(processed_docs)


def lda_topic_word(article):
    with open('tf_vectorizer.pkl', 'rb') as f:
        tf_vectorizer = pickle.load(f)

    with open('lda.pkl', 'rb') as f:
        lda = pickle.load(f)

    tokenizer = Tokenizer.factory("english")
    tokens = tokenizer.tokenize_by_word(article, apply_token_filters=True)
    doc = " ".join([unit.token for unit in tokens])

    # convert to
    tok = tf_vectorizer.transform([" ".join(doc)])

    topic_doc_distribution = lda.transform(tok)
    topic = np.argmax(topic_doc_distribution)
    topic_word_distribution = lda.exp_dirichlet_component_[topic].tolist()
    return {word: topic_word_distribution[idx] for idx, word in enumerate(tf_vectorizer.get_feature_names())}


dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
document = dataset.data[5012]
x = lda_topic_word(document)
for x, y in x.items():
    print(x, y)
