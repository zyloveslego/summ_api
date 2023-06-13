from app.web_api.bert_service.service.client import BertClient
from scipy import spatial

bc = BertClient()
a = bc.encode(['Obama get', 'The President greets the press in Chicago',
               'A major scientific report issued by 13 federal agencies on Friday presents the starkest warnings to date of the consequences of climate change for the United States, predicting that if significant steps are not taken to rein in global warming,'])
print(a)
result_1 = 1 - spatial.distance.cosine(a[0], a[1])
result_2 = 1 - spatial.distance.cosine(a[1], a[2])
result_3 = 1 - spatial.distance.cosine(a[0], a[2])
print("*"*4)
print(bc.encode(["obama get"])[0])
print(result_2)
print(result_3)