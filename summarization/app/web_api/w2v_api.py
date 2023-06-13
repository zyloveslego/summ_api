from flask import Flask
from flask_restful import Resource, Api, reqparse
from gensim.models import KeyedVectors
import argparse
import base64
from itertools import combinations as _combinations


try:
    from app import definitions
    definition_imported = True
except ImportError:
    print("Not able to find definition file, please specify the args manually")
    print("use python w2v_api.py -help for detail")
    definition_imported = False

parser = reqparse.RequestParser()

def filter_words(words):
    if words is None:
        return
    return [word for word in words if word in model.vocab]


class NSimilarity(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ws1', type=str, required=True, help="Word set 1 cannot be blank!", action='append')
        parser.add_argument('ws2', type=str, required=True, help="Word set 2 cannot be blank!", action='append')
        args = parser.parse_args()
        return str(model.n_similarity(filter_words(args['ws1']),filter_words(args['ws2'])))


class Similarity(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('w1', type=str, required=True, help="Word 1 cannot be blank!")
        parser.add_argument('w2', type=str, required=True, help="Word 2 cannot be blank!")
        args = parser.parse_args()
        return str(model.similarity(args['w1'], args['w2']))


class WMD(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('s1', type=str, required=True, help="Word 1 cannot be blank!")
        parser.add_argument('s2', type=str, required=True, help="Word 2 cannot be blank!")
        args = parser.parse_args()
        return str(model.wmdistance(args['s1'], args['s2']))


class PairwiseWMD(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("sentence_list", type=str, required=True, help="sentence_list cannot be blank!")
        args = parser.parse_args()
        sentence_list = args["sentence_list"].split("#")
        pair_similarity = dict()
        for s1, s2 in _combinations(sentence_list, 2):
            pair_similarity[s1 + "#" + s2] = str(model.wmdistance(s1, s2))
        return pair_similarity


class MostSimilar(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('positive', type=str, required=False, help="Positive words.", action='append')
        parser.add_argument('negative', type=str, required=False, help="Negative words.", action='append')
        parser.add_argument('topn', type=int, required=False, help="Number of results.")
        args = parser.parse_args()
        pos = filter_words(args.get('positive', []))
        neg = filter_words(args.get('negative', []))
        t = args.get('topn', 10)
        pos = [] if pos == None else pos
        neg = [] if neg == None else neg
        t = 10 if t == None else t
        print("positive: " + str(pos) + " negative: " + str(neg) + " topn: " + str(t))
        try:
            res = model.most_similar_cosmul(positive=pos, negative=neg, topn=t)
            return res
        except Exception as e:
            print(e)


class PairwiseWordSimilarity(Resource):
    def post(self):
        """
        input: {"word_list":"w1#w2#w3"}
        output: {"word1#word2":"0.233", "word2#word3":"0.233" }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('word_list', type=str, required=True, help="word list cannot be blank")
        args = parser.parse_args()
        word_list = args["word_list"].split("#")
        pair_similarity = dict()
        for w1, w2 in _combinations(word_list, 2):
            try:
                score = str(model.similarity(w1, w2))
            except KeyError:
                score = 0.35
            pair_similarity[w1+"#"+w2] = str(score)
        return pair_similarity


class Model(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('word', type=str, required=True, help="word to query.")
        args = parser.parse_args()
        try:
            res = model[args['word']]
            res = base64.b64encode(res)
            return res
        except Exception as e:
            print(e)
            return


app = Flask(__name__)
api = Api(app)


@app.errorhandler(404)
def page_not_found(error):
    return "page not found"


@app.errorhandler(500)
def raise_error(error):
    return error


if __name__ == '__main__':
    """
    run the program use definition file: python -m app.utils.w2v_api --model modelpath --host IP --port portno --lang cn
    run the program with manual settings: python -m app.utils.w2v_api --model modelpath --host IP --port portno --lang cn
    run the program without definition file : python w2v_api.py --model modelpath --host IP --port portno --lang cn
    or chinese must have para -lang, or it may give encoding error
    test 1: http://127.0.0.1:9004/w2v/similarity?w1=Sushi&w2=Japanese
    test 2: http://127.0.0.1:9004/w2v/most_similar?positive=sugar&topn=2
    """
    global model
    # ----------- Parsing Arguments ---------------
    p = argparse.ArgumentParser()
    p.add_argument("--model", help="Path to the trained model")
    p.add_argument("--binary", help="Specifies the loaded model is binary")
    p.add_argument("--host", help="Host name (default: localhost)")
    p.add_argument("--port", help="Port (default: 8080)")
    p.add_argument("--path", help="Path (default: no path)")
    p.add_argument("--lang", help="Language (default: english) (opt chinese, english) (no wmd for cn)")
    args = p.parse_args()

    if definition_imported:
        model_path = args.model if args.model else definitions.W2V_EN_MODEL_PATH
        host = args.host if args.host else definitions.W2V_API_WEB_API_URL
        path = args.path if args.path else definitions.W2V_API_WEB_API_PATH
        port = int(args.port) if args.port else definitions.W2V_API_WEB_API_PORT
        lang = args.lang if args.lang else definitions.W2V_API_LANG
    else:
        model_path = args.model if args.model else None
        host = args.host if args.host else "localhost"
        path = args.path if args.path else "/w2v"
        port = int(args.port) if args.port else 8080
        lang = args.lang if args.lang else "english"

    print(model_path)
    if not model_path:
        raise Exception("Usage: word2vec-apy.py --model path/to/the/model [--host host --port 1234]")
    print("-----------------------Loading model!-----------------------")
    model = KeyedVectors.load_word2vec_format(model_path)
    api.add_resource(NSimilarity, path+'/n_similarity')
    api.add_resource(Similarity, path+'/similarity')
    api.add_resource(MostSimilar, path+'/most_similar')
    api.add_resource(PairwiseWordSimilarity, path+'/pairwise_word_similarity')
    api.add_resource(PairwiseWMD, path+'/pairwise_wmd')
    api.add_resource(Model, path+'/model')
    print("-----------------------Model has been load successfully!-----------------------")
    print("server start at http://" + host + ":" + str(port) + path + "/")
    if lang == "english" or lang == "en":
        api.add_resource(WMD, path+'/wmd')
    app.run(host=host, port=port)
