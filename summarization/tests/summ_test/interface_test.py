import requests

# url = 'http://127.0.0.1:8000/my_summ/'
url = 'http://wangserver.ddns.net:8631/my_summ/'

# text
text = open("/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/summarization/tests/summ_test/test_data/swr.txt").read()
data = {
    'text': text,
}
r = requests.post(url, data=data)
print(r.json())


# 返回json dict
# {'sentence':
#   [
#       [sentence_index(int), sentence(str), sentence_score(float), sentence_rank(int)],
#       ...
#   ]
# }

