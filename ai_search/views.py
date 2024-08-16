from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
# import json
# # import chromadb
# import re
# # from openai import OpenAI
# import sqlite3
# import requests
# import json
# from rank_bm25 import BM25Okapi
import string

from scholarly import scholarly


def fetch_google_scholar_data(search_query):
    search_results = scholarly.search_pubs(search_query)

    papers = []
    for i in range(15):
        paper = next(search_results)
        papers.append(paper)

    response_data = {"files": []}

    for paper in papers:
        try:
            if 'arxiv' in paper['pub_url']:
                paper['pub_url'] = paper['pub_url'].replace('abs', 'pdf')

            response_data["files"].append({
                "name": paper['bib']['title'],
                "abstract": paper['bib']['abstract'],
                "url": paper['pub_url']
            })
        except:
            pass

    return response_data


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


# search main function
@csrf_exempt
@api_view(['POST'])
def ai_search(request):
    query_params = request.data
    print(query_params['message'])
    # paper_ids = ['d749a42c-4c52-44a3-8fe8-32e20b722927', '6de82c95-fa62-4bac-a10f-63a9b2d14c5a']
    # response_data = {paper_ids[0]: ["snapshot1", "snapshot2"], paper_ids[1]: ["snapshot1", "snapshot2"]}
    #
    # response_data = {"files": [
    #     {
    #         "name": "name1",
    #         "abstract": "abstract1",
    #         "url": "paper_url1"
    #     },
    #     {
    #         "name": "name2",
    #         "abstract": "abstract2",
    #         "url": "paper_url2"
    #     }
    # ]}

    response_data = fetch_google_scholar_data(query_params['message'])

    import random
    random_integer = random.randint(1, 100)
    if random_integer % 2 == 0:
        return JsonResponse(response_data)
    else:
        response_data = {"chat": "This is a chat message."}
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
