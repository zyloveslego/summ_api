import requests

url = 'http://wangserver.ddns.net:8631/my_summ/'

# input text
text = open().read()
data = {
    'text': text,
}

r = requests.post(url, data=data).json()
print(r)

# json dict structure
# {'sentence':
#   [
#       [sentence_index(int), sentence(str), sentence_score(float), sentence_rank(int)],
#       ...
#   ]
# }
