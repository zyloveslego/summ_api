# Keywords

## Requirement
TODO: 

## Test Error
RUN 有两个w2v的test的时候会报错。 因为没有设置好w2v。

## Module
* Keyword (app.keywords.keyword)
    * 基本初始化
         * KeyWord.basic_init(language)
         * 全部使用默认设置，只需要设置语言。
    * 自定义初始化：
        * 需要 inject 4个模块 language，tokenizer，combinator，weighting
        * language "chinese" 或者 "english"
        * tokenizer 包含分词处理，删除stopwords, 给每个词做词性标签等功能。可以当做是专门为keywords服务的Utils类。下面是参数说明。
            * language，同以上
            * candidate_generation_method，关键词是单词还是词组，"WORD"是单词，"PHRASE"是词组，词组还没有实现。
            * 调用工厂: Tokenizer.factory(language, candidate_generation_method)
        * combinator 用于关键词的合并，在关键词生成后，进行关键词合并。下面是参数设置。
            * language，同以上
            * max_combine_length 合并的最长限制，中文预设值为2，即最多两个词相连，英文预设没有限制。
            * remove 接受boolean，
                * True代表，合并时不限制词相连的个数，只是在返回时删除掉所有超过限制的词，不管分数的高低。
                * False代表，在生成时，就限制词相连的个数。
            * allow_duplication 接受boolean，
                * 只有在remove为false时才有效果。
                * 在合并时，时候可以用已经用掉的keywords
                * ex. allow I like you very much. => I like, like you, you very, very much. length = 2
                * ex. not allow I like you very much. => I like, you very, much. length = 2
        * weighting 用于生成图时，如何连接边
            * CO_OCCUR 用co-occurrence + 相似词语义边 连接图。
            * CO_OCCUR_W2V 用co-occurrence + W2V的语义边 连接图。
    * 调用关键词提取
        * extract(text, ratio=0.2, words=None, split=False, scores=False, combination=True, textrank_original=True)
        * 参数说明：
            * ratio: 0-1之间的数字，返回关键词的百分比。当ratio=1时，返回全部
            * words: 关键词的个数。
            * scores boolean, 返回关键词时，同时返回分数。
            * combination boolean, 关键词是否合并。默认为合并。
            * textrank_original，关键词如何删除。
                * True时表示，删除发生在生成关键词之后，但在合并关键词之前。会导致合并的关键词较少。
                * False时表示，删除发生在合并关键词之后，去top K的合并关键词。

* W2V Service
    * app.definition里包含了W2V的基本设置。
    * W2V有两个调用方法。
        1. 由程序生成一个class
        2. 先运行程序生成一个web api形式的W2V service。
    * utils中的tovec_service是调用方法。
    * utils中的w2v_api是web api。 用了flask，flask_restful
    * 详情请看程序doc
    
    
-------------------------
Update 1.5