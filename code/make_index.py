import os
import math
import json
import pandas as pd

def process_text(text, stopwords, index_url):
    words = text.split(" ")
    for word in words:
        if word not in stopwords:
            if word not in index_url:
                index_url[word] = 1
            else:
                index_url[word] += 1

# 读取数据
df = pd.read_csv("./index.csv", encoding='utf-8-sig')
df = df.set_index('url')
df = df.fillna("")

# 检查并创建目录
if not os.path.exists("./frequency"):
    os.mkdir("./frequency")

# 读取停用词
with open('./stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()
    add_stopwords = ['要闻', '新闻', '新闻网', '讯', '...']
    stopwords += add_stopwords

# 初始化索引
index = {}

# 遍历数据框的每一行
for url, row in df.iterrows():
    index[url] = {}
    
    # 处理标题、描述、文本和新闻来源的文本
    process_text(row['title'], stopwords, index[url])
    process_text(row['description'], stopwords, index[url])
    process_text(row['text'], stopwords, index[url])
    process_text(row['news_from'], stopwords, index[url])
    
    # 删除空字符串
    if index[url].get('') is not None:
        del index[url]['']

# 计算词频
word_frequency = {}
for url, words in index.items():
    for word, frequency in words.items():
        word_frequency[word] = word_frequency.get(word, 0) + 1

# 构建倒排索引
inverted_index = {}
for url, words in index.items():
    for word, frequency in words.items():
        if word not in stopwords:
            inverted_index.setdefault(word, {}).update({url: frequency})

# 计算逆文档频率
word_idf = {}
for url, frequency_dict in index.items():
    for word, frequency in frequency_dict.items():
        word_idf[word] = math.log(len(index) / frequency)

# 计算tf
tf = {}
for url, words in index.items():
    tf[url] = {word: words[word] for word in words}

# 计算tf-idf
tf_idf = {}
for url, words in index.items():
    tf_idf[url] = {word: frequency * word_idf[word] for word, frequency in words.items()}

# 保存JSON文件
def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

save_json('./frequency/inverted_index.json', inverted_index)
save_json('./frequency/tf-idf.json', tf_idf)
save_json('./frequency/word_frequency.json', word_frequency)
save_json('./frequency/word_idf.json', word_idf)
save_json('./frequency/tf.json', tf)

# 仅处理标题的部分
index_title_only = {}
for url, row in df.iterrows():
    index_title_only[url] = {}
    process_text(row['title'], stopwords, index_title_only[url])

word_frequency_title_only = {}
for url, words in index_title_only.items():
    for word, frequency in words.items():
        word_frequency_title_only[word] = word_frequency_title_only.get(word, 0) + 1

inverted_index_title_only = {}
for url, words in index_title_only.items():
    for word, frequency in words.items():
        if word not in stopwords:
            inverted_index_title_only.setdefault(word, {}).update({url: frequency})

word_idf_title_only = {}
for url, frequency_dict in index_title_only.items():
    for word, frequency in frequency_dict.items():
        word_idf_title_only[word] = math.log(len(index_title_only) / frequency)

tf_title_only = {}
for url, words in index_title_only.items():
    tf_title_only[url] = {word: words[word] for word in words}

tf_idf_title_only = {}
for url, words in index_title_only.items():
    tf_idf_title_only[url] = {word: frequency * word_idf_title_only[word] for word, frequency in words.items()}

save_json('./frequency/inverted_index_title_only.json', inverted_index_title_only)
save_json('./frequency/tf-idf_title_only.json', tf_idf_title_only)
save_json('./frequency/word_frequency_title_only.json', word_frequency_title_only)
save_json('./frequency/word_idf_title_only.json', word_idf_title_only)
save_json('./frequency/tf_title_only.json', tf_title_only)
