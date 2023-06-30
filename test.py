import json

import requests

# url = 'http://wangserver.ddns.net:8631/my_summ/'
url = 'http://127.0.0.1:8000/my_summ/from_dict'
url = 'http://wangserver.ddns.net:8631/essaygrader/'


# input text
# text = open().read()
text = {'0': 'The Kremlin warned ex-patriots to evacuate areas close to several Russian-assigned European nuclear bomb targets, RadarOnline.com has learned.', '1': 'In a chilling development to come as Vladimir Putin\'s ongoing war against Ukraine continues to escalate, a close ally of the 70-year-old Russian leader suggested that nuclear attacks against Europe may "become necessary" and that Russian expatriates needed to be warned before the potential strikes.', '2': 'Segey Karaganov, who chairs the Council of Foreign and Defense Policy, also revealed that the Kremlin may approve nuclear strikes as a way to force countries to back down from aiding Ukraine.', '3': "Nuclear concerns recently arose after both the United Kingdom and the United States supplied Ukraine with weaponry to combat Putin's invading Russian forces.", '4': 'Putin is allegedly "offering nuclear weapons" to countries that join the war to help Moscow.'}

text = open(
    "/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/summarization/tests/summ_test/test_data/text03.txt").read()


# data = {
#     'text': json.dumps(text),
# }

text = "this is a test"

data = {
    'text': text,
}

print(data)

r = requests.post(url, data=data).json()
print(r)

# json dict structure
# {'sentence':
#   [
#       [sentence_index(int), sentence(str), sentence_score(float), sentence_rank(int)],
#       ...
#   ]
# }

# import openai
#
# # Create your views here.
# def get_essay_grade():
#     text = open("/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/summarization/tests/summ_test/test_data/pyramid.txt").read()
#
#
#     openai.api_key = "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"
#     ft_model = 'ada:ft-librum2:set8-conventions-2023-06-20-03-52-43'
#     res = openai.Completion.create(model=ft_model, prompt=text + '->', max_tokens=1, temperature=0)
#     print(int(res['choices'][0]['text'])/2)
#
#     pass
#
# get_essay_grade()

