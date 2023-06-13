from flask import Flask
from flask_restful import Resource, Api, reqparse
import argparse
from app.keywords.keyword import KeyWord
from app.summ.model.kw_summarizer import KWSummarizer

parser = reqparse.RequestParser()


def filter_words(words):
    if words is None:
        return
    return [word for word in words if word in model.vocab]


class Summary(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True, help="input text", action='append')
        parser.add_argument('limit_method', type=str, required=True,
                            help="limitation method can be length_ratio, word_count, sentence_count, sentence_ratio",
                            action='append')

        parser.add_argument('limitation', type=float, required=True, help="limitation number", action='append')

        args = parser.parse_args()
        text = args['text'][0]
        limit_method = args['limit_method'][0]
        limitation = args["limitation"][0]

        if limit_method == "length_ratio":
            summary = summarizer.summarize(text, length_ratio=limitation)
        elif limit_method == "word_count":
            summary = summarizer.summarize(text, word_count=limitation)
        elif limit_method == "sentence_count":
            summary = summarizer.summarize(text, sentence_count=limitation)
        elif limit_method == "sentence_ratio":
            summary = summarizer.summarize(text, sentence_ratio=limitation)
        else:
            summary = "error"
        if summary != "error":
            summary = summarizer.format_result_by_para(text, summary)
            print(summary)
        return summary


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
    p.add_argument("--host", help="Host name (default: localhost)")
    p.add_argument("--port", help="Port (default: 8080)")
    p.add_argument("--lang", help="Language (default: english) (opt chinese, english) (no wmd for cn)")
    args = p.parse_args()

    host = args.host if args.host else "localhost"
    port = int(args.port) if args.port else 8080
    lang = args.lang if args.lang else "chinese"

    customized_textrank = KeyWord.basic_init(language=lang, weighting_method="CO_OCCUR")
    summarizer = KWSummarizer.factory(language=lang, summarizer_name="TW",
                                      customized_textrank=customized_textrank)

    api.add_resource(Summary, '/summary')
    app.run(host=host, port=port)
