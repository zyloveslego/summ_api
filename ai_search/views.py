from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
# import json
# # import chromadb
# import re
from openai import OpenAI
# import sqlite3
# import requests
import json
# from rank_bm25 import BM25Okapi
import string
import sqlite3
import http.client

from scholarly import scholarly

client = OpenAI()

conn = sqlite3.connect('search_history.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        searchId TEXT PRIMARY KEY,
        last_search_history TEXT,
        raw_data TEXT
    )
''')


conn.commit()

conn.close()

print("Table created successfully.")


def fetch_google_scholar_data(search_query):
    conn = http.client.HTTPSConnection("serpapi.webscrapingapi.com")

    conn.request("GET", "/v1?engine=google_scholar&api_key=&q=" + search_query)

    res = conn.getresponse()
    data = res.read()

    search_result = json.loads(data.decode("utf-8"))['organic_results']

    conn.request("GET",
                 "/v1?engine=google_scholar&api_key=&q=" + search_query + "&start=10")

    res = conn.getresponse()
    data = res.read()

    search_result10 = json.loads(data.decode("utf-8"))['organic_results']

    paper_titles = []
    for index, paper_info in enumerate(search_result):
        paper_titles.append(str(index + 1) + '. ' + paper_info['title'])

    for index, paper_info in enumerate(search_result10):
        paper_titles.append(str(index + 11) + '. ' + paper_info['title'])

    raw_data = {"files": []}

    for index, paper_info in enumerate(search_result):
        if 'arxiv' in paper_info['link']:
            paper_info['link'] = paper_info['link'].replace('abs', 'pdf')

        raw_data["files"].append({
            "name": paper_info['title'],
            "abstract": paper_info['snippet'],
            "url": paper_info['link'],
            "index": index + 1
        })

    for index, paper_info in enumerate(search_result10):
        if 'arxiv' in paper_info['link']:
            paper_info['link'] = paper_info['link'].replace('abs', 'pdf')

        raw_data["files"].append({
            "name": paper_info['title'],
            "abstract": paper_info['snippet'],
            "url": paper_info['link'],
            "index": index + 11
        })

    return paper_titles, raw_data


def get_user_intent(search_query):
    prompt = """
    You are a professional researcher. I will provide you with a query, and you need to determine which of the following three categories it falls into:

    1. A clear search query, such as "network security."
    2. An acronym with multiple meanings or query which is unclear, such as "KAN."
    3. An additional search condition, such as "add keywords, large language model."

    Here's the query: 
    """

    messages = [{"role": "user", "content": prompt + search_query}]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "user_intent",
                "description": "Based on the user query, tell me which type the query belongs to.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent_type": {
                            "type": "string",
                            "description": "The type stated above which user query satisfied, return 1, 2 or 3.",
                        },
                        "hint": {
                            "type": "string",
                            "description": """If it is type 2, an acronym with multiple meanings or query which is unclear, 
                            write a "short" hint to ask user, guess what they might wanna ask. 
                            For example, if user ask KAN, you can answer: I am not sure about this acronym, you might wanna ask Knowledge Acquisition Network?
                            The guess should be related to academic.
                            If not type 2, return None.
                            """
                        },
                        "add_info": {
                            "type": "string",
                            "description": """If it is type 3, adding condition, extract the adding info.
                            For example, if query is "add keywords, large language model", then extract "large language model"
                            Simply extract the additional search condition and remove those adding words. 
                            If not type 3, return None.""",

                        }
                    },
                    "required": ["intent_type", "add_info", "hint"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    json_response = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

    return json_response


def get_related_titles(search_query, titles):
    prompt = """
    You are a professional researcher. I will give you 20 article titles with id, and a user query. 
    you tell me which titles are relevant to user query.

    Here's the query: {}

    Here are the titles: {}

    Return ids and titles of which titles are relevant to user query.
    """

    messages = [{"role": "user", "content": prompt.format(search_query, '\n'.join(titles))}]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_related_titles",
                "description": "Based on the user query, return ids and titles which are relevant to user query, and explain why.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "The ids of titles which are relevant to user query. If none of them are relevant, return None",
                        },
                        "titles": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "The titles which are relevant to user query. If none of them are relevant, return None",
                        },
                        "reasons": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "Why these title matches the query.",
                        }
                    },
                    "required": ["ids", "titles", "reasons"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    # print(json.loads(response.choices[0].message.tool_calls[0].function.arguments)['reasons'])

    titles = json.loads(response.choices[0].message.tool_calls[0].function.arguments)['titles']
    ids = json.loads(response.choices[0].message.tool_calls[0].function.arguments)['ids']
    if "None" in titles or "None" in ids or titles == [] or ids == []:
        return []

    return json.loads(response.choices[0].message.tool_calls[0].function.arguments)['ids']

# import numpy as np

# db_name = 'arxiv_papers'
# # initial ChromaDB
# chromadb_client = chromadb.PersistentClient()
# chromadb_collection = chromadb_client.get_collection(name=db_name)

#
# def query_cossim(user_query, n_results=100):
#     """
#     get result from chromadb using cos similarity
#     :param:
#         my_query: query text, str
#         n_results: return top k, default 10
#     :return:
#         query_result dict from chromadb, which contain 'documents' and 'distances'
#     """
#     query_result = chromadb_collection.query(query_texts=[user_query], n_results=n_results)
#     return query_result
#
#
# def cal_BM25(query, documents: list):
#     """
#     calculate BM25 score
#     :param:
#         query: user query
#     :param:
#         documents: list of documents
#     :return:
#         BM25 score between query and documents
#     """
#
#     def pre_process_BM25(input_data):
#         """
#         simple pre-process in BM25
#         :param:
#             input_data: list or str of doc
#         :return:
#             processed doc
#         """
#         if isinstance(input_data, str):
#             translator = str.maketrans('', '', string.punctuation)
#             return input_data.translate(translator).lower()
#         elif isinstance(input_data, list):
#             translator = str.maketrans('', '', string.punctuation)
#             return [item.translate(translator).lower() for item in input_data]
#         else:
#             return "Unsupported input type"
#
#     tokenized_corpus = [pre_process_BM25(doc).split(" ") for doc in documents]
#
#     bm25 = BM25Okapi(tokenized_corpus)
#     tokenized_query = pre_process_BM25(query).split(" ")
#     doc_scores = bm25.get_scores(tokenized_query)
#
#     return doc_scores

def get_last_search_history(search_id):
    # 连接到SQLite数据库
    conn = sqlite3.connect('search_history.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    # 查询数据库中是否存在给定的searchId
    cursor.execute('''
        SELECT last_search_history FROM search_history WHERE searchId = ?
    ''', (search_id,))

    # 获取查询结果
    result = cursor.fetchone()

    if result:
        # 如果查询结果存在，取出并转为数组
        last_search_history = json.loads(result[0])
        # print(type(last_search_history))
        # print("Search history found:", last_search_history)
    else:
        # 如果查询结果不存在，新建一条数据，last_search_history 为 []
        last_search_history = []
        cursor.execute('''
            INSERT INTO search_history (searchId, last_search_history)
            VALUES (?, ?)
        ''', (search_id, json.dumps(last_search_history)))

        # 提交事务
        conn.commit()

        # print("No search history found. New entry created.")

    # 关闭连接
    conn.close()

    return last_search_history

def update_last_search_history(search_id, last_search_history):
    # 连接到SQLite数据库
    conn = sqlite3.connect('search_history.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    # 将新的last_search_history列表转换为JSON字符串
    last_search_history_str = json.dumps(last_search_history)

    # 更新数据库中对应searchId的记录
    cursor.execute('''
        UPDATE search_history
        SET last_search_history = ?
        WHERE searchId = ?
    ''', (last_search_history_str, search_id))

    # 提交事务
    conn.commit()

    # 关闭连接
    conn.close()


def save_list_as_string(search_id, paper_dict):
    # 连接到SQLite数据库，如果数据库不存在则创建
    conn = sqlite3.connect('search_history.db')
    cursor = conn.cursor()

    # list_as_string = str(paper_list)
    raw = json.dumps(paper_dict)

    cursor.execute('''
        UPDATE search_history
        SET raw_data = ?
        WHERE searchId = ?
    ''', (raw, search_id))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()


def load_raw_data(search_id):
    # 连接到SQLite数据库
    conn = sqlite3.connect('search_history.db')
    cursor = conn.cursor()

    # 从表中选择数据
    cursor.execute('SELECT raw_data FROM search_history where searchId = ?', (search_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    else:
        return None


def search_main(search_query, search_id):
    last_search_history = get_last_search_history(search_id)
    user_intent_type = get_user_intent(search_query)
    print(user_intent_type)
    search_query = search_query.replace(" ", "+")
    if user_intent_type['intent_type'] == '1':
        # paper_titles = fetch_google_scholar_data(search_query)
        temp_paper_titles, temp_raw_data = fetch_google_scholar_data(search_query)

        save_list_as_string(search_id, temp_raw_data)

        re_search_result = get_related_titles(search_query, temp_paper_titles)

        return_infos = []
        for name_url in load_raw_data(search_id)['files']:
            if str(name_url['index']) in re_search_result:
                return_infos.append(
                    {'name': name_url['name'], 'abstract': name_url['abstract'], 'url': name_url['url']})

        # print(re_search_result)

        print("-" * 20)
        update_last_search_history(search_id, re_search_result)

        return {"files": return_infos}

    elif user_intent_type['intent_type'] == '2':
        return {"chat": user_intent_type['hint']}
        # return user_intent_type['hint']
    elif user_intent_type['intent_type'] == '3':
        if user_intent_type['add_info'] == None or user_intent_type['add_info'] == 'None':
            temp_paper_titles, temp_raw_data = fetch_google_scholar_data(search_query)

            re_search_result = get_related_titles(search_query, temp_paper_titles)

            return_infos = []
            for name_url in load_raw_data(search_id)['files']:
                if str(name_url['index']) in re_search_result:
                    return_infos.append(
                        {'name': name_url['name'], 'abstract': name_url['abstract'], 'url': name_url['url']})

            # print(re_search_result)

            print("-" * 20)
            update_last_search_history(search_id, re_search_result)

            return {"files": return_infos}
        else:
            print('add_info')
            print(user_intent_type['add_info'])
            print(last_search_history)
            if last_search_history == []:
                return {"chat": "Sorry, there is no related papers."}
                # return "Sorry, there is no related papers."

            temp_paper_titles = []
            for name_url in load_raw_data(search_id)['files']:
                if str(name_url['index']) in last_search_history:
                    temp_paper_titles.append(str(name_url['index']) + '. ' + name_url['name'])


            add_search_result = get_related_titles(user_intent_type['add_info'], temp_paper_titles)
            # add_search_titles = [last_search_history[int(i)] for i in add_search_result]

            print("add_search_result")
            print(add_search_result)

            return_infos = []
            for name_url in load_raw_data(search_id)['files']:
                if str(name_url['index']) in add_search_result:
                    return_infos.append(
                        {'name': name_url['name'], 'abstract': name_url['abstract'], 'url': name_url['url']})

            print(add_search_result)

            print("-" * 20)
            update_last_search_history(search_id, add_search_result)

            return {"files": return_infos}


# search main function
@csrf_exempt
@api_view(['POST'])
def ai_search(request):
    # {'searchId': '99099072-3345-4fad-8dc6-34dac0d00d25', 'message': 'large language model', 'history': []}
    # searchId
    query_params = request.data
    search_query = query_params['message']
    search_id = query_params['searchId']
    print(query_params['message'])

    # response_data = fetch_google_scholar_data(query_params['message'])
    response_data = search_main(search_query, search_id)
    print(response_data)

    return JsonResponse(response_data)


# # Create your views here.
#
# # ai_search
# @csrf_exempt
# @api_view(['POST'])
# def ai_search(request):
#     query_dict = request.data
#
#     print("this is ai_search")
#
#     print(query_dict)
#
#     # (1, 'c956f28f-a93d-4d4f-9306-c6eddaf738c4', 0, '{"keywords": ["IoT"], "authors": [], "time": null, "rest_info": "IoT"}')
#     # 根据searchId查询history result
#     if 'history' in query_dict.keys() and len(query_dict['history']) != 0 and 'searchId' in query_dict['history'][0]:
#         conn = sqlite3.connect('/home/data/ssd-1/zy/dooyeed/AI_search.db')
#         cursor = conn.cursor()
#         searchId = query_dict['history'][0]['searchId']
#         query = """
#             SELECT * FROM searchHistory
#             WHERE searchId = ?
#             ORDER BY searchRound ASC
#         """
#         cursor.execute(query, (searchId,))
#         history_result = cursor.fetchall()
#         cursor.close()
#     else:
#         history_result = []
#
#     # 根据history result查询
#     if len(history_result) == 0:
#         # history里的id在本地数据库中没有
#         MAX_ATTEMPTS = 3
#         attempt = 0
#         while attempt < MAX_ATTEMPTS:
#             try:
#                 extracted_query_dict = analysis_query(query_dict['message'])
#             except Exception as e:
#                 print("Exception:", e)
#                 attempt += 1
#
#             else:
#                 break
#         else:
#             print("max attempt")
#             from nltk.tokenize import word_tokenize
#             extracted_query_dict = {'authors': ['None'], 'time': None, 'rest_info': query_dict['message'],
#                                     'keywords': word_tokenize(query_dict['message'])}
#         print(extracted_query_dict)
#         # extracted_query_dict = analysis_query(query_dict['message'])
#         combined_query_result = ai_search_main(extracted_query_dict)
#         pass
#
#
#     else:
#         # history里的id在本地数据库中有; 根据之前的记录,按顺序查询
#         flag = 0
#         combined_query_result = []
#         for i in history_result:
#             # print(json.loads(i[3]))
#             extracted_query_dict = json.loads(i[3])
#             if flag == 0:
#                 combined_query_result = ai_search_main(extracted_query_dict)
#                 flag = flag + 1
#                 pass
#             else:
#                 if combined_query_result == []:
#                     pass
#                 else:
#                     combined_query_result = ai_search_main_with_ids(extracted_query_dict, combined_query_result)
#                     pass
#
#         MAX_ATTEMPTS = 3
#         attempt = 0
#         while attempt < MAX_ATTEMPTS:
#             try:
#                 extracted_query_dict = analysis_query(query_dict['message'])
#             except Exception as e:
#                 print("Exception:", e)
#                 attempt += 1
#
#             else:
#                 break
#         else:
#             print("max attempt")
#             from nltk.tokenize import word_tokenize
#             extracted_query_dict = {'authors': ['None'], 'time': None, 'rest_info': query_dict['message'],
#                                     'keywords': word_tokenize(query_dict['message'])}
#         combined_query_result = ai_search_main_with_ids(extracted_query_dict, combined_query_result)
#
#         pass
#
#     conn = sqlite3.connect('/home/data/ssd-1/zy/dooyeed/AI_search.db')
#     cursor = conn.cursor()
#     new_data = (query_dict['searchId'], len(history_result), json.dumps(extracted_query_dict))
#     insert_query = """
#         INSERT INTO searchHistory (searchId, searchRound, searchFormat)
#         VALUES (?, ?, ?)
#     """
#     cursor.execute(insert_query, new_data)
#     conn.commit()
#     cursor.close()
#
#     return_dict = combine_snapshot(combined_query_result)
#
#     # print(type(query))
#     # print(query['message'])
#     # paper_ids = ['d749a42c-4c52-44a3-8fe8-32e20b722927', '6de82c95-fa62-4bac-a10f-63a9b2d14c5a']
#     # response_data = {paper_ids[0]: ["snapshot1", "snapshot2"], paper_ids[1]: ["snapshot1", "snapshot2"]}
#
#     return JsonResponse(return_dict)
#
#
# # data save into vector database
# @csrf_exempt
# @api_view(['POST'])
# def savetodb(request):
#     query = request.data
#
#     print("this is savetodb")
#
#     # print(type(query))
#     print(len(query['metadatas']))
#     # print(query['file'])
#     print(query['file']['summary'])
#     print(query['file']['dooyeedSummary'])
#
#     # print(len(query['metadatas']['context']))
#     # print(len(query['metadatas']['embedding']))
#     #
#     # assert len(query['metadatas']['context']) == len(query['metadatas']['embedding'])
#
#     priority_method = 0
#     priority_target = 0
#     priority_both = 0
#
#     conn = sqlite3.connect('/home/data/ssd-1/zy/dooyeed/AI_search.db')
#     cursor = conn.cursor()
#     # searchHistory / PAPERS
#     db_query = """
#         SELECT title FROM PAPERS
#     """
#     cursor.execute(db_query)
#     history_result = cursor.fetchall()
#
#     cursor.close()
#
#     if query['file']['documentTitle'] in [i[0] for i in history_result]:
#         print(True)
#         response_data = {"success": True}
#         return JsonResponse(response_data)
#     else:
#         print(False)
#
#
#     if query['file']['articlePublishedAt'] is None:
#         time = ""
#     else:
#         time = int(query['file']['articlePublishedAt'][:4])
#
#     for i in query['metadatas']:
#         author_list = [j['author'] for j in query['file']['authors']]
#         # print(",".join(author_list))
#
#         if i['type'] == "method":
#             current_priority = priority_method
#         elif i['type'] == "target":
#             current_priority = priority_target
#         else:
#             current_priority = priority_both
#
#         if i['embedding'] is None or i['embedding'] == []:
#             print("there is null")
#
#         # chromadb_client = chromadb.PersistentClient(path="/home/data/ssd-1/zy/dooyeed/")
#         # collection = chromadb_client.get_collection(name="AI_search", metadata={"hnsw:space": "cosine"})
#
#         collection.add(
#             documents=[i['context'] + "&&&" + ",".join(author_list)],
#             embeddings=[i['embedding']],
#             metadatas=[{"id": i['id'], "type": i['type'], "time": time, 'priority': current_priority,
#                         "snapshot": json.dumps(i['snapshot'])}],
#             ids=[i['id'] + "_" + str(i['type'] + "_" + str(current_priority))]
#         )
#
#         if i['type'] == "method":
#             priority_method = priority_method + 1
#         elif i['type'] == "target":
#             priority_target = priority_target + 1
#         else:
#             priority_both = priority_both + 1
#
#     conn = sqlite3.connect('/home/data/ssd-1/zy/dooyeed/AI_search.db')
#     cursor = conn.cursor()
#     insert_data_sql = '''
#     INSERT INTO PAPERS (paper_id, title, published, summary, author_name, method, target, method_target, snapshot)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
#     '''
#
#     my_snapshot = []
#     for i in query['metadatas']:
#         for j in i['snapshot']:
#             my_snapshot.append(j)
#
#     my_snapshot = list(set(my_snapshot))
#
#     # 数据
#     data = (query['file']['id'],
#             query['file']['documentTitle'],
#             time,
#             query['file']['dooyeedSummary'],
#             ', '.join([i['author'] for i in query['file']['authors']]),
#             ', '.join([i['context'] for i in query['metadatas'] if i['type'] == 'method']),
#             ', '.join([i['context'] for i in query['metadatas'] if i['type'] == 'target']),
#             ', '.join([i['context'] for i in query['metadatas'] if i['type'] == 'method|target']),
#             str(my_snapshot),
#             )
#
#     cursor.execute(insert_data_sql, data)
#     conn.commit()
#     cursor.close()
#
#     response_data = {"success": True}
#
#     return JsonResponse(response_data)
