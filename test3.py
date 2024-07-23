import threading
import json
import requests


url1 = 'http://wangserver.ddns.net:8631/my_summ/'
url1 = 'http://127.0.0.1:8000/my_summ/'
# not dict
with open('/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/test_data/plain_text_2.txt', 'r') as file:
    txt_file_contents = file.read()
    # print(txt_file_contents)

# encoded_text = txt_file_contents.encode('latin-1')
encoded_text = txt_file_contents.encode('utf-8')

# print(encoded_text)

data = {
    'text': encoded_text,
}


r = requests.post(url1, data=data)
print(r)
for i in json.loads(r.text)['sentence_rank']:
    print(i)


# def send_post_request():
#     url1 = 'http://wangserver.ddns.net:8631/my_summ/from_dict'
#     # not dict
#     with open('/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/english30_2.json', 'r') as file:
#         txt_file_contents = file.read()
#         # text = json.load(file)
#         # print(txt_file_contents)
#
#     # encoded_text = txt_file_contents.encode('latin-1')
#     encoded_text = txt_file_contents.encode('utf-8')
#     # print(encoded_text)
#
#     text = json.loads(encoded_text)
#
#     # # print(encoded_text)
#     # temp = json.loads(encoded_text)
#     temp_arr = []
#     for k, v in text.items():
#         temp_arr.append(v)
#         # break
#     #
#     repeated_arr = temp_arr * 3
#     sentences_dict = {}
#     for j, sentence in enumerate(repeated_arr):
#         sentences_dict[str(j)] = sentence
#     encoded_text = json.dumps(sentences_dict, ensure_ascii=False, indent=4)
#     # # print(encoded_text)
#
#     small_dict = {key: text[key] for key in list(text)[:5000]}
#     # print(small_dict)
#
#
#     # data = {
#     #     'text': json.dumps(text),
#     # }
#
#     data = {
#         'text': encoded_text,
#     }
#
#
#
#
#     r = requests.post(url1, data=data)
#     print(r)
#
# import time
# start_time = time.time()
# threads = []
# for i in range(0, 10):
#     thread = threading.Thread(target=send_post_request, )
#     thread.start()
#     threads.append(thread)
#
# for thread in threads:
#     thread.join()
#
# end_time = time.time()
#
# # 计算代码运行时间
# execution_time = end_time - start_time
# print("代码运行时间为: ", execution_time, "秒")
