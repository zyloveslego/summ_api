from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import copy
import openai
import tiktoken
from langdetect import detect


# 判断输入的文本类型和语言，将相应的文本进行翻译

# input:latex -> 直接翻译
# input:pdf -> 用余的接口转为html翻译
# input:word -> docx2pdf转为html后翻译

# detect language, zh or en, call corresponding prompt


# 得到文件类型
def get_doc_type():
    pass


# 得到文本语言
def get_doc_lang(input_string):
    return detect(input_string)


# 切分chunk代码
def cut_into_slices(input_text, model, chunk, enter_encoding):
    encoding = tiktoken.encoding_for_model(model)
    all_encoding = encoding.encode(input_text)

    # all_encoding = all_encoding[0:100]
    # all_encoding[30] = 198
    # all_encoding[80] = 198

    encoded_slices = []
    index = 0
    temp_index = 0
    temp = []
    temp_slice = []
    while index < len(all_encoding):
        if len(temp) >= chunk and temp_slice != []:
            encoded_slices.append(temp_slice)

            temp = []
            temp_slice = []
            index = temp_index
        elif len(temp) >= chunk and temp_slice == []:
            encoded_slices.append(temp)

            temp = []
            temp_slice = []
            temp_index = 0
        elif len(temp) < chunk and all_encoding[index] == enter_encoding:
            temp.append(all_encoding[index])
            index = index + 1

            temp_slice = copy.deepcopy(temp)
            temp_index = index
        else:
            temp.append(all_encoding[index])
            index = index + 1
    encoded_slices.append(temp)
    return encoded_slices


# 翻译输入来的文本
# input: string
# output: string
def html_translate(html_string):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    enter_encoding = encoding.encode("\n")[0]
    chunk = 2000
    model = "gpt-3.5-turbo"
    lang = get_doc_lang(html_string)

    encoded_slices = cut_into_slices(html_string, model, chunk, enter_encoding)
    decoded_slices = []
    for i in encoded_slices:
        decoded_slices.append(encoding.decode(i))

    if lang == "zh-cn":
        prompt = "将下面的文本翻译成英文并且保留html格式: "
    else:
        prompt = "Translate the following content into Chinese and keep the original html format: "



    openai.api_key = ""
    translated_slices = ""
    for i in decoded_slices:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt + i},
            ]
        )
        translated_slices = translated_slices + response["choices"][0]["message"]["content"]

        # break

    # print(prompt)
    # print(translated_slices)

    return translated_slices

    pass


# Create your views here.
@csrf_exempt
def my_translate(request):
    doc = ""
    if request.method == 'POST':
        doc = request.POST.get('doc')

    if request.method == 'GET':
        return JsonResponse({})

    translated_doc = html_translate(doc)

    my_response = {'translated_doc': translated_doc}

    return JsonResponse(my_response)
