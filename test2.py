import json
import sys
import time
import requests
#
url1 = 'http://wangserver.ddns.net:8631/my_summ/'
url2 = 'http://wangserver.ddns.net:8631/my_summ/from_dict'
#
# url1 = 'http://127.0.0.1:8000/my_summ/'
url2 = 'http://127.0.0.1:8000/my_summ/from_dict'
# url2 = 'http://127.0.0.1:8000/my_summ/from_dict_ks'
#
# not dict
# with open('/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/sentence_ranking_str.txt', 'r') as file:
#     txt_file_contents = file.read()
#     # print(txt_file_contents)
#
# # encoded_text = txt_file_contents.encode('latin-1')
# encoded_text = txt_file_contents.encode('utf-8')
#
# print(encoded_text)
#
# data = {
#     'text': encoded_text,
# }
#
#
# r = requests.post(url1, data=data)
# print(r)
# for i in json.loads(r.text)['sentence_rank']:
#     print(i)
#
#


#
# # dict
with open('/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/test_data/NOUN_ascii_dict_2.json', 'r') as file:
    text = json.load(file)


# print(text)
# with open('/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/sentence_ranking.json', 'r') as file:
#     text = json.load(file)
import string

# def remove_punctuation(text):
#     # 创建一个转换表，将标点符号映射为None
#     translator = str.maketrans('', '', string.punctuation)
#     # 使用translate方法去除标点符号
#     return text.translate(translator)

# print(len(text))
# total = 0
# for i in text.items():
#     index, word = i
#     total = total + len(remove_punctuation(word))
#
# print(total)


# small_dict = {key: text[key] for key in list(text)[:500]}
# # print(small_dict)
# print(len(small_dict))

# dictionary = eval(text)

# text = {"0": "\u5370\u5149\u5927\u5e2b\u6587\u9214\u83c1\u83ef\uf93f", "2": "\u5370\u5370\u5149\u5149\u5927\u5927\u5e2b\u5e2b\u6587\u6587\u9214\u9214\u83c1\u83c1\u83ef\u83ef\u9304\u9304", "3": "\u5370\u5149\u5927\u5e2b\u64b0"}

data = {
    'text': json.dumps(text),
}


# sys.exit(0)

# for k, v in text.items():
#     print(k, v)

start_time = time.time()

r = requests.post(url2, data=data)
print(r)
for i in json.loads(r.text)['sentence_rank']:
    print(i)

end_time = time.time()

# 计算代码运行时间
execution_time = end_time - start_time
print("代码运行时间为: ", execution_time, "秒")
# return_dict = json.loads(r.text)['sentence_rank']
#
# key_list=list(text.keys())
# val_list=list(text.values())

# print(key_list)

# for i in return_dict:
#     i[0] = key_list[val_list.index(i[1])]
#
# print(return_dict)
#
# #
# #
# # #
# # from nltk.data import load
# # tokenizer = load('tokenizers/punkt/{0}.pickle'.format('english'))
# #
# # print(tokenizer)