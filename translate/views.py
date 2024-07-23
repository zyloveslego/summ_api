from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import copy
import openai
import tiktoken
from langdetect import detect
from rest_framework.decorators import api_view

# from rest_framework.views import APIView

import tiktoken
from langdetect import detect
import requests
import re
import time


# 判断输入的文本类型和语言，将相应的文本进行翻译

# input:latex -> 直接翻译
# input:pdf -> 用余的接口转为html翻译
# input:word -> docx2pdf转为html后翻译

# detect language, zh or en, call corresponding prompt


@csrf_exempt
@api_view(['POST'])
def translate_dict(request):
    if request.method == 'GET':
        return JsonResponse({})

    content_data = request.data.get("content")
    target_lang = request.data.get("tar_lang")

    # print(content_data)
    # print(target_lang)

    model = "gpt-4"

    # test_data = {
    #     1: "Potential harms of large language models can be mitigated by watermarking model output, i.e., embedding signals into generated text that are invisible to humans but algorithmically detectable from a short span of tokens.",
    #     2: "We propose a watermarking framework for proprietary language models.",
    #     3: "The watermark can be embedded with negligible impact on text quality, and can be detected using an efficient opensource algorithm without access to the language model API or parameters.",
    #     4: "The watermark works by selecting a randomized set of “green” tokens before a word is generated, and then softly promoting use of green tokens during sampling.",
    #     5: "We propose a statistical test for detecting the watermark with interpretable p-values, and derive an informationtheoretic framework for analyzing the sensitivity of the watermark.",
    #     6: "We test the watermark using a multi-billion parameter model from the Open Pretrained Transformer (OPT) family, and discuss robustness and security",
    #     }

    # request_data = {"tar_lang": "Chinese", "content": test_data}

    if target_lang == None:
        target_lang = "Chinese"

    def post_process(translated_piece):
        try:
            # Define a regular expression pattern to match text between square brackets
            pattern = r'\"(.*?)\"'

            # Use re.findall to find all matches of the pattern in the string
            matches = re.findall(pattern, translated_piece)

            return matches[0]

        except IndexError:
            return translated_piece

    def translate_one_sentence(sentence, target_lang="Chinese", model="gpt-4", ):
        prompt = """
                Translate the each of the sentence to {}:

                "{}"

                """
        url = 'http://34.206.94.45:7231/chat_completion'
        system_prompt = "You are an academic translator"
        # print(prompt.format(user_prompt))
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt.format(target_lang, sentence)}]
        # messages = json.dumps(messages)
        data = {'messages': messages, 'config': {'model': model, 'temperature': 0}}
        response = requests.post(url, json=data, timeout=60)
        result = response.json()
        # 返回结果
        return result['result']

    def translate_one_return_dict(input_data, target_lang="Chinese"):
        all_translated_array = []

        # translate each piece
        for sentence in input_data.values():
            translated_piece = translate_one_sentence(sentence, target_lang)
            # print(translated_piece)
            all_translated_array.append(post_process(translated_piece))

        return all_translated_array

    translated_sentences = translate_one_return_dict(content_data, target_lang)

    # print(translated_sentences)

    content = {}

    for index, value in enumerate(content_data.values()):
        content.setdefault(index + 1, [translated_sentences[index], value])

    response_data = {"tar_lang": target_lang, "createdAt": time.time(), "content": content}

    # print(response_data)

    return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})


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


def save_uploaded_file(file: InMemoryUploadedFile, file_path: str) -> None:
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    file.close()


# 翻译输入来的文本
@csrf_exempt
@api_view(['POST'])
def html_translate(request):
    if request.method == 'GET':
        return JsonResponse({})

    my_file = request.FILES.get("html_file")
    lang = request.data.get("lang")

    save_uploaded_file(my_file, "./upload_file/" + str(my_file))

    # from django.core.files.storage import default_storage

    #  Saving POST'ed file to storage
    # print(request.FILES)
    # file = request.FILES['html_file']
    # file_name = default_storage.save(file.name, file)

    # #  Reading file from storage
    # my_file = default_storage.open(file_name)

    file_content = open("./upload_file/" + str(my_file)).read()
    pdf2html_url = 'http://wangserver.ddns.net:5501/convertPDFtoHTML01'

    import requests
    r = requests.post(pdf2html_url, files={'files': file_content})
    html_string = r.content

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    enter_encoding = encoding.encode("\n")[0]
    chunk = 2000
    model = "gpt-3.5-turbo"
    # lang = get_doc_lang(html_string)

    encoded_slices = cut_into_slices(html_string, model, chunk, enter_encoding)
    decoded_slices = []
    for i in encoded_slices:
        decoded_slices.append(encoding.decode(i))

    # if lang == "zh-cn":
    #     prompt = "将下面的文本翻译成英文并且保留html格式: "
    # else:
    prompt = "Translate the following content into" + lang + "and keep the original html format: "

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

    my_response = {'translated_doc': translated_slices}

    return JsonResponse(my_response)

    # return translated_slices

    pass


@csrf_exempt
@api_view(['POST'])
def html_translate_string(request):
    if request.method == 'GET':
        return JsonResponse({})

    html_string = request.data.get("html_string")
    lang = request.data.get('lang')

    # html_string = request.POST.get('html_string')
    # lang = request.POST.get('lang')

    print(html_string)
    print(lang)

    # save_uploaded_file(my_file, "./upload_file/" + str(my_file))
    #
    # file_content = open("./upload_file/" + str(my_file)).read()
    # pdf2html_url = 'http://wangserver.ddns.net:5501/convertPDFtoHTML01'

    # import requests
    # r = requests.post(pdf2html_url, files={'files': file_content})
    # html_string = r.content

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    enter_encoding = encoding.encode("\n")[0]
    chunk = 2000
    model = "gpt-3.5-turbo"
    # lang = get_doc_lang(html_string)

    encoded_slices = cut_into_slices(html_string, model, chunk, enter_encoding)
    decoded_slices = []
    for i in encoded_slices:
        decoded_slices.append(encoding.decode(i))

    # if lang == "zh-cn":
    #     prompt = "将下面的文本翻译成英文并且保留html格式: "
    # else:
    prompt = "Translate the following content into" + lang + "and keep the original html format: "

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

    my_response = {'translated_doc': translated_slices}

    return JsonResponse(my_response)

    pass
