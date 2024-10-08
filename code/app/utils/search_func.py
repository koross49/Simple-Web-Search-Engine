import math
from jieba import cut_for_search
from app.public_const import *

key_valid_number = 500  # 有效关键词数量


# 统计词频
def computeTF(word_set, split):
    tf = dict.fromkeys(word_set, 0)
    for word in split:
        if word in word_set:
            tf[word] += 1
    for word, cnt in tf.items():
        tf[word] = math.log10(cnt + 1)  # TF = log10(N + 1) 减少文本长度带来的影响
    return tf


# 计算IDF
def computeIDF(tf_list):
    idf_dict = dict.fromkeys(tf_list[0], 0)  # 词为key，初始值为0
    N = len(tf_list)  # 总文档数量
    for tf in tf_list:  # 遍历字典中每一篇文章
        for word, count in tf.items():  # 遍历当前文章的每一个词
            if count > 0:  # 当前遍历的词语在当前遍历到的文章中出现
                idf_dict[word] += 1  # 包含词项tj的文档的篇数df+1
    for word, Ni in idf_dict.items():  # 利用公式将df替换为逆文档频率idf
        idf_dict[word] = round(math.log10(N / Ni), 4)  
    return idf_dict  # 返回逆IDF字典


# 计算tf-idf
def computeTFIDF(tf, idfs):  # tf词频,idf逆文档频率
    tfidf = {}
    for word, tfval in tf.items():
        tfidf[word] = tfval * idfs[word]
    return tfidf


def length(key_list):
    num = 0
    for i in range(len(key_list)):
        num = num + key_list[i][1] ** 2
    return round(math.sqrt(num), 2)

# 基础搜索
def main(input_word: str, history_words: list, is_title_only: bool = False) -> list[tuple[str, float]]:

    # 关键词分词
    split_input = list(cut_for_search(input_word))
    split_input.sort()
    if '' in split_input:
        split_input.remove('')
    if ' ' in split_input:
        split_input.remove(' ')

    # 历史记录分词
    split_history = []
    for i in range(len(history_words)):
        temp_split = list(cut_for_search(history_words[i]))
        for i in temp_split:
            if i in ['', ' ']:
                pass
            elif i not in split_history:
                split_history.append(i)

    # 判断搜索模式
    if not is_title_only:
        tf_dict = tf
        idfs = idf
        word_sets = word_set
    else:
        tf_dict = tf_title_only
        idfs = idf_title_only
        word_sets = word_set_title_only

    tfidf_dict = {}  
    for k, v in tf_dict.items():
        tfidf_dict[k] = computeTFIDF(v, idfs)

    key_tfidf_dict = {}  
    for k, v in tfidf_dict.items():
        key_tfidf_dict[k] = sorted(tfidf_dict[k].items(), key=lambda d: d[1], reverse=True)[:key_valid_number]
    key_tfidf_list = list(key_tfidf_dict.values())  # 将结果转化为list
    key_tfidf_url_list = list(key_tfidf_dict.keys())  
    len_key_tfidf_url_list = len(key_tfidf_url_list)

    tf_input = computeTF(word_sets, split_input)  # 查询的tf
    tfidf_input = computeTFIDF(tf_input, idfs)  # 查询的tf-idf
    key_input = sorted(tfidf_input.items(), key=lambda d: d[1], reverse=True)[:key_valid_number]  # 查询的前100个关键词
    len_key_input = length(key_input)

    if len_key_input == 0:
        raise KeyError  # 如果输入关键词和历史记录都为无法匹配到关键词，则返回错误

    tf_history = computeTF(word_sets, split_history)  # 历史记录的tf
    tfidf_history = computeTFIDF(tf_history, idfs)  # 历史记录的tf-idf
    key_history = sorted(tfidf_history.items(), key=lambda d: d[1], reverse=True)[:key_valid_number]  # 历史记录的前100个关键词
    len_key_history = length(key_history)

    # 余弦相似度计算
    key_results = []
    key_results_index: list[int] = []  # 用于存储index，方便history_words的调用
    for i in range(len_key_tfidf_url_list):  # 遍历每个文档
        num = 0
        _key_tfidf_list = key_tfidf_list[i]
        for _key_input in key_input:  # 遍历每个关键输入词
            if _key_input[1] != 0:
                for __key_tfidf_list in _key_tfidf_list:  # 遍历每个文档内的每个关键词
                    if _key_input[0] == __key_tfidf_list[0]:  # 若为相同单词
                        num = num + _key_input[1] * __key_tfidf_list[1]
        cos = round(num / (len_key_input * length(_key_tfidf_list)), 4)
        key_results.append((key_tfidf_url_list[i], cos))  # 存储第i个文档的余弦相似度
        if cos > 0:
            key_results_index.append(i)
    if len(history_words) > 0:  # 没有历史记录时不计算历史记录的相似度
        history_results_dict = {}
        for i in key_results_index:  # 遍历每个文档
            num = 0
            _key_tfidf_list = key_tfidf_list[i]
            for _key_history in key_history:  # 遍历每个关键输入词
                if _key_history[1] != 0:
                    for __key_tfidf_list in _key_tfidf_list:  # 遍历每个文档内的每个关键词
                        if _key_history[0] == __key_tfidf_list[0]:  # 若为相同单词
                            num = num + _key_history[1] * __key_tfidf_list[1]
            history_results_dict[i] = ((key_tfidf_url_list[i], (round(num / (len_key_history * length(_key_tfidf_list)), 4))))  # 存储第i个文档的余弦相似度

        results = []
        for i in range(len_key_tfidf_url_list):
            if key_results[i][1] == 0:  
                pass
            elif j := history_results_dict.get(i):
                results.append((key_results[i][0], key_results[i][1] + j[1] / 10))  # 历史记录的权重为0.1
            else:
                results.append((key_results[i][0], key_results[i][1]))
        results = sorted(results, key=lambda d: d[1], reverse=True)
    else:
        results = []
        for i in range(len_key_tfidf_url_list):
            results.append((key_results[i][0], key_results[i][1]))
        results = sorted(results, key=lambda d: d[1], reverse=True)

    return_list = []
    for result in results:
        if result[1] > 0:
            return_list.append((result[0], result[1]))
    return return_list

