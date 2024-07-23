# 中文pdf 30页 1100句
# 英文pdf 30页 1400句
# 分别计算句子数量

# import PyPDF2
#
#
# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with open(pdf_path, "rb") as file:
#         reader = PyPDF2.PdfReader(file)
#         num_pages = len(reader.pages)
#         for page_number in range(num_pages):
#             page = reader.pages[page_number]
#             text += page.extract_text()
#     return text
#
#
# # 指定PDF文件路径
# pdf_path = "/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/test_data/2312.07913.pdf"
#
# # 提取文本
# pdf_text = extract_text_from_pdf(pdf_path)
# # print(pdf_text)
#
# from nltk.tokenize import sent_tokenize
#
# sentences = sent_tokenize(pdf_text)
#
# print(len(sentences))


import requests

# Specify the URL
url = 'http://wangserver.ddns.net:8631/ai_search/'
# url = 'http://127.0.0.1:8000/ai_search/'

# Parameters to be sent in the GET request
data = {
    'title': 'foo',
    'body': 'bar',
    'userId': 1
}

# Send a GET request with parameters
response = requests.post(url, json=data)

# Print the response content
print(response.json())


