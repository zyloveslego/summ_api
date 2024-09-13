import threading
import json
import requests


# url1 = 'http://wangserver.ddns.net:9013/ai_search/'
url1 = 'http://127.0.0.1:8000/ai_search/'

data = {
    # 'message': 'large language model',
    'message': 'add keywords, survey',
    'searchId': 'abv'
}


r = requests.post(url1, data=data)
print(r.text)

