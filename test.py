# from nltk.data import load
#
# text_list = """
# Certain analytical queries, such as “how many active users are on the ‘web’ platform”, may generate SQL queries that do not conform to the database’s actual values if generated naively. For example, the where clause in the response might bewhere platform=’web’ as opposed to the correct where platform=’WEB’. To address such issues, unique values of low-cardinality columns which would frequently be used for this kind of filtering are processed and incorporated into the table schema, so that the LLM can make use of this information to generate precise SQL queries.
# """
#
# sentence_list = []
# tokenizer = load('tokenizers/punkt/{0}.pickle'.format('english'))
# paragraphs = [p for p in text_list.split('\n') if p]
# for paragraph in paragraphs:
#     sentence_list.extend(tokenizer.tokenize(paragraph))
#
# for i in paragraphs:
#     print(i)
#
# for i in sentence_list:
#     print(i)

import json
import sys
import time
import requests

url1 = 'http://wangserver.ddns.net:8631/my_summ/'
url2 = 'http://wangserver.ddns.net:8631/my_summ/from_dict'


# dict
with open('/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/test_data/NOUN_ascii_dict_2.json', 'r') as file:
    text = json.load(file)

data = {
    'text': json.dumps(text),
}


start_time = time.time()

r = requests.post(url2, data=data)
print(r)
for i in json.loads(r.text)['sentence_rank']:
    print(i)

end_time = time.time()

# 计算代码运行时间
execution_time = end_time - start_time
print("代码运行时间为: ", execution_time, "秒")
