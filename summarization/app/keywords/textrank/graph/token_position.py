from collections import defaultdict

UNIFORM = 0
INVERTED_PYRAMID = 1
PYRAMID = 2
HOURGLASS = 3
CALCULATED = 4


def get_token_position_weight(token_list, article_structure):
    if article_structure == INVERTED_PYRAMID:
        return token_position_weight_inverse_pyramid_reciprocal_of_index(token_list)

    if article_structure == PYRAMID:
        return token_position_weight_pyramid_index(token_list)

    if article_structure == HOURGLASS:
        return token_position_weight_hour_glass_quadratic(token_list)

    if article_structure == CALCULATED:
        return my_token_position_weight(token_list)

def my_token_position_weight(my_token_list, article_structure, model, text):
    # input -> class 'app.keywords.textrank.syntactic_unit.SyntacticUnit' -> token list
    # output -> { xxx: score, ... }
    # {'hello': 1.0, 'john': 0.5, 'said': 0.4238029954286499, 'today': 0.25, ...}
    # 词所属的句子与原文的相似度 / sum(句子与原文的相似度 * 该句子的lemma词)

    # 我的返回结构
    # [[1.原句，2.token_list], ...]
    from sklearn.metrics.pairwise import cosine_similarity
    # import time
    # start = time.time()
    # 计算分母
    # 全文的embedding
    # print(text)
    embedding_text = model.encode(text)
    denominator = 0
    # start1 = time.time()
    # print("程序执行时间", start1-start)

    temp_embedding = []
    for i in my_token_list:
        temp_embedding.append(model.encode(i[0]))

    temp_cos = []
    for index, i in enumerate(my_token_list):
        temp_cos.append(cosine_similarity([temp_embedding[index]], [embedding_text])[0][0])

    # 开始计算分母
    for index, i in enumerate(my_token_list):
        # embedding = model.encode(i[0])
        # print(cosine_similarity([embedding], [embedding_text])[0][0])
        denominator = denominator + temp_cos[index] * len(i[1])

    # print(denominator)
    # start2 = time.time()
    # print("程序执行时间", start2 - start1)


    # 计算分子
    token_dict = {}
    for index, i in enumerate(my_token_list):
        for word in i[1]:
            # print(word)
            # print(word.token)
            _word = word.token
            # embedding = model.encode(i[0])
            sim = temp_cos[index]
            if _word not in token_dict:
                token_dict[_word] = sim
            else:
                token_dict[_word] = token_dict[_word] + sim
        # break

    # print("dict length" + str(len(token_dict)))
    # start3 = time.time()
    # print("程序执行时间", start3 - start2)
    # print(token_dict)
    for key in token_dict:
        token_dict[key] = token_dict[key] / denominator

    # end = time.time()
    # print("程序执行时间", end-start3)

    return token_dict


def token_position_weight_inverse_pyramid_reciprocal_of_index(token_list):
    token_dict = defaultdict(int)
    for token in token_list:
        _word = token.token
        _position = token.index + 1
        weight = 1.0 / float(_position)
        token_dict[_word] += weight
    return token_dict


def token_position_weight_inverse_pyramid_quadratic(token_list, x=20):
    # use a quadratic function for weight calculating
    # w(i) = a(i-n)**2 + b
    # we have w(n) = b, so we want to let w(1) = x*w(n), where x is a parameter, we can set to 5
    # and Sum of w(i) = 1
    # a = 12 / ((n-1)*n*(7n-5))
    # b = 3(n-1) / (7n-5) * n
    n = max([token.index for token in token_list]) + 1
    # set w(1) = x * w(n)
    a = 6*(x-1) / (n*(n-1)*(2*x*n + 4*n - 5 -x))
    b = a/4 * (1-n)**2
    token_dict = defaultdict(int)
    for token in token_list:
        _word = token.token
        _position = token.index + 1
        weight = a*(_position-n)**2 + b
        # print(weight*1000, _position)
        token_dict[_word] += weight
    return token_dict


# def token_position_weight_inverse_pyramid_linear(token_list, x=5):
#     # use a quadratic function for weight calculating
#     # w(i) = ai + b
#     # we have w(n) = b, so we want to let w(1) = x*w(n), where x is a parameter, we can set to 5
#     # and Sum of w(i) = 1
#     n = max([token.index for token in token_list]) + 1
#     a = 2*(n-1) / ((x+1)*n*(1-n))
#     b = 2*(1-x*n) / ((x+1)*n*(1-n))
#     print(a, b)
#     token_dict = defaultdict(int)
#     for token in token_list:
#         _word = token.token
#         _position = token.index + 1
#         weight = a*(_position) + b
#         # print(weight*1000, _position)
#         token_dict[_word] += weight
#     return token_dict


def token_position_weight_pyramid_index(token_list):
    token_dict = {}
    for token in token_list:
        _word = token.token
        _position = token.index + 1
        if _word not in token_dict:
            token_dict[_word] = float(_position)
        else:
            token_dict[_word] = token_dict[_word] + float(_position)
    return token_dict


def token_position_weight_hour_glass_reciprocal_of_index(token_list):
    n = max([token.index for token in token_list])+1
    token_dict = defaultdict(int)
    for token in token_list:
        _word = token.token
        _position = token.index + 1
        weight = 1.0 / float(_position) if _position < n//2 else 1.0 / float(n+1-_position)
        token_dict[_word] += weight
    return token_dict


def token_position_weight_hour_glass_step(token_list):
    n = max([token.index for token in token_list])+1
    A = 120/49/n
    B = 40/49/n
    C = 60/49/n
    token_dict = defaultdict(int)
    for token in token_list:
        _word = token.token
        _position = token.index + 1
        if _position <= n*0.1:
            weight = A
        elif _position <= n*0.85:
            weight = B
        else:
            weight = C
        token_dict[_word] += weight
    return token_dict


def token_position_weight_hour_glass_quadratic(token_list):
    n = max([token.index for token in token_list])+1
    m = n // 2
    c = 1 / (sum([(i + 1 - m)**2 for i in range(n)]) + 1)
    token_dict = defaultdict(int)
    for token in token_list:
        _word = token.token
        _position = token.index + 1
        weight = c * (_position-m)**2 + c
        token_dict[_word] += weight
    return token_dict
