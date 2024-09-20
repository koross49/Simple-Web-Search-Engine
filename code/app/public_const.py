import json
import os
import pandas as pd

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

path = r'./frequency'
path2 = r'./'

# 读取advanced_search_index.csv
advanced_search_index = pd.read_csv(os.path.join(path2, 'advanced_search_index.csv'))
advanced_search_index.fillna('', inplace=True)
advanced_search_index.set_index('url', inplace=True)

# 读取inverted_index.json
inverted_index = read_json_file(os.path.join(path, 'inverted_index.json'))

# 读取word_frequency.json
word_frequency = read_json_file(os.path.join(path, 'word_frequency.json'))
word_set = sorted(set(word_frequency.keys()))

# 读取word_idf.json
idf = read_json_file(os.path.join(path, 'word_idf.json'))

# 读取tf.json
tf = read_json_file(os.path.join(path, 'tf.json'))

# 读取tf-idf.json
tf_idf = read_json_file(os.path.join(path, 'tf-idf.json'))

# 读取inverted_index_title_only.json
inverted_index_title_only = read_json_file(os.path.join(path, 'inverted_index_title_only.json'))

# 读取word_frequency_title_only.json
word_frequency_title_only = read_json_file(os.path.join(path, 'word_frequency_title_only.json'))
word_set_title_only = sorted(set(word_frequency_title_only.keys()))

# 读取word_idf_title_only.json
idf_title_only = read_json_file(os.path.join(path, 'word_idf_title_only.json'))

# 读取tf_title_only.json
tf_title_only = read_json_file(os.path.join(path, 'tf_title_only.json'))

# 读取tf-idf_title_only.json
tf_idf_title_only = read_json_file(os.path.join(path, 'tf-idf_title_only.json'))

# 读取url-title
url_title_df = pd.read_csv(os.path.join(path2, 'title_url.csv'), encoding='utf-8', index_col='url')
url_title_df1 = pd.read_csv(os.path.join(path2, 'title_url.csv'), encoding='utf-8')

# 读取page_rank.csv
page_rank_df = pd.read_csv(os.path.join(path2, 'page_rank.csv'), encoding='utf-8', index_col='url')
