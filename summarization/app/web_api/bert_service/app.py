import argparse
import sys

from app.web_api.bert_service.bert.extract_features import PoolingStrategy
from app.web_api.bert_service.service.server import BertServer


# to run the service : python -m app.web_api.bert_service.app -model ~/Downloads/uncased_L-12_H-768_A-12/ -num_worker=4
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-model_dir', type=str, required=True,
                        help='directory of a pretrained BERT model')
    parser.add_argument('-max_seq_len', type=int, default=50,
                        help='maximum length of a sequence')
    parser.add_argument('-num_worker', type=int, default=1,
                        help='number of server instances')
    parser.add_argument('-max_batch_size', type=int, default=256,
                        help='maximum number of sequences handled by each worker')
    parser.add_argument('-port', type=int, default=5555,
                        help='port number for C-S communication')
    parser.add_argument('-pooling_layer', type=int, default=-2,
                        help='the encoder layer that receives pooling')
    parser.add_argument('-pooling_strategy', type=PoolingStrategy.from_string,
                        default=PoolingStrategy.REDUCE_MEAN, choices=list(PoolingStrategy),
                        help='the pooling strategy for generating encoding vectors')

    args = parser.parse_args()
    param_str = '\n'.join(['%20s = %s' % (k, v) for k, v in sorted(vars(args).items())])
    print('usage: %s\n%20s   %s\n%s\n%s\n' % (' '.join(sys.argv), 'ARG', 'VALUE', '_' * 50, param_str))
    return args


if __name__ == '__main__':
    args = get_args()
    server = BertServer(args)
    server.start()
    server.join()