import sys, string, random, numpy
from nltk.corpus import reuters
from summarization.app.topic_modeling.llda import LLDA
from optparse import OptionParser
from functools import reduce
from summarization.app.topic_modeling.bbc_dataset import BBCDataset
import pickle
import numpy as np

parser = OptionParser()
parser.add_option("--alpha", dest="alpha", type="float", help="parameter alpha", default=1)
parser.add_option("--beta", dest="beta", type="float", help="parameter beta", default=0.01)
parser.add_option("-k", dest="K", type="int", help="number of topics", default=5)
parser.add_option("-i", dest="iteration", type="int", help="iteration count", default=300)
parser.add_option("-s", dest="seed", type="int", help="random seed", default=0)
parser.add_option("-n", dest="samplesize", type="int", help="dataset sample size", default=100)
(options, args) = parser.parse_args()
random.seed(options.seed)
numpy.random.seed(options.seed)

# idlist = random.sample(reuters.fileids(), options.samplesize)
#
# labels = []
# corpus = []
# for id in idlist:
#     labels.append(reuters.categories(id))
#     corpus.append([x.lower() for x in reuters.words(id) if x[0] in string.ascii_letters])
#     reuters.words(id).close()
# labelset = list(set(reduce(list.__add__, labels)))
#
# options.alpha = 50 / (len(labelset) + 1)
# llda = LLDA(options.alpha, options.beta, options.K)
# llda.set_corpus(corpus, labels)
#
# print(corpus[0])
# print(labels[0])
# print("M=%d, V=%d, L=%d, K=%d" % (len(corpus), len(llda.vocas), len(labelset), options.K))
# llda.inference(options.iteration)
#
# phi = llda.phi()
# for k, label in enumerate(labelset):
#     print ("\n-- label %d : %s" % (k + 1, label))
#     for w in numpy.argsort(-phi[k + 1])[:10]:
#         print("%s: %.4f" % (llda.vocas[w], phi[k + 1, w]))
#
# ss = llda.fold(corpus[30])

# ---------------------------------


def bbc_training():
    news = BBCDataset().news

    labels = []
    corpus = []
    for x, label in news:
        corpus.append(x)
        labels.append([label])

    print(corpus[0])
    print(labels[0])

    labelset = list(set(reduce(list.__add__, labels)))
    options.alpha = 50 / (len(labelset) + 1)
    llda = LLDA(options.alpha, options.beta, options.K)
    llda.set_corpus(corpus, labels)

    print("M=%d, V=%d, L=%d, K=%d" % (len(corpus), len(llda.vocas), len(labelset), options.K))
    llda.inference(options.iteration)

    phi = llda.phi()
    for k, label in enumerate(labelset):
        print("\n-- label %d : %s" % (k + 1, label))
        for w in numpy.argsort(-phi[k + 1])[:10]:
            print("%s: %.4f" % (llda.vocas[w], phi[k + 1, w]))

    with open('llda.pkl', 'wb') as f:
        pickle.dump(llda, f)

# ---------------------------------


def llda_topic_word(article):
    with open('/Users/hao/Code/Summarization/app/topic_modeling/llda.pkl', 'rb') as f:
        llda = pickle.load(f)

    doc_topic_distribution = llda.fold(article)
    topic = np.argmax(doc_topic_distribution)
    phi = llda.phi()[topic]

    word_topic = {}
    for x in set(article):
        id = llda.find_term_id(x)
        if not id:
            continue
        word_topic[x] = phi[id]

    return topic, word_topic


# news = BBCDataset().news
#
# labels = []
# corpus = []
# for x, label in news:
#     corpus.append(x)
#     labels.append([label])
#
# word_topic = llda_topic_word(corpus[10])
#
# print(word_topic)
