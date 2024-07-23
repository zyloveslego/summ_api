import threading
import json
import sys
import time
import requests


# 定义要执行的工作
def do_work(work_id):
    print(work_id)
    url1 = 'http://wangserver.ddns.net:8631/my_summ/'
    url2 = 'http://wangserver.ddns.net:8631/my_summ/from_dict'

    with open('/test_data/decoded_content.txt', 'r') as file:
        text = json.load(file)

    small_dict = {key: text[key] for key in list(text)[:1000]}

    data = {
        'text': json.dumps(small_dict),
    }

    start_time = time.time()

    r = requests.post(url2, data=data)
    print(r)
    # for i in json.loads(r.text)['sentence_rank']:
    #     print(i)

    end_time = time.time()

    # 计算代码运行时间
    execution_time = end_time - start_time
    print("代码运行时间为: ", execution_time, "秒")


# 创建并启动线程
threads = []
for i in range(15):
    t = threading.Thread(target=do_work, args=(i,))
    threads.append(t)
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

print("All work finished")
