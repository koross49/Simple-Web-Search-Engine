from util import load_doc
from jieba import cut_for_search
import csv
import networkx as nx
import pandas as pd
import math
import glob
import os

analyzer = cut_for_search  # 初始化分词器

url_total_list = []
url_list_disk = {}

def cut_word(doc):
    new_doc = {}
    if doc['title'] is not None:
        new_doc['title'] = " ".join(analyzer(doc['title']))
    else:
        new_doc['title'] = None
    if doc['text'] is not None:
        new_doc['text'] = " ".join(analyzer(doc['text']))
    else:
        new_doc['text'] = None
    if doc['description'] is not None:
        new_doc['description'] = " ".join(analyzer(doc['description']))
    else:
        new_doc['description'] = None

    new_doc['id'] = doc['id']
    new_doc['date'] = doc['date']
    new_doc['url'] = doc['url']
    #new_doc['page_links'] = doc['page_links']
    new_doc['category'] = doc['category']
    new_doc['page_rank'] = 0
    new_doc['news_from'] = doc['news_from']
    
    return new_doc


def save_in_csv(docs, csv_filename, fields=None):
    # 写入 CSV 文件
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        # 创建 CSV writer 对象
        csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
        # 写入头部
        csv_writer.writeheader()
        # 写入数据
        for doc in docs:
            csv_writer.writerow(doc)


if __name__ == '__main__':
    json_files = glob.glob(os.path.join('data/news', '*.json'))
    json_count = len(json_files)
    docs = []
    docs_clean = []
    title_urls = []
    url_prs = []
    for i in range(1,json_count):
        doc = load_doc(i)
        # 保存原始数据
        doc_clean = load_doc(i)
        doc_clean['page_rank'] = 0
        del doc_clean['page_links']
        docs_clean.append(doc_clean)

        # 保存标题和url和description
        title_url = {}
        title_url['title'] = doc['title']
        title_url['url'] = doc['url']
        title_url['description'] = doc['description']
        title_url['category'] = doc['category']
        title_urls.append(title_url)

        # 保存url和page_rank
        url_pr = {}
        url_pr['url'] = doc['url']
        url_pr['page_rank'] = 0
        url_prs.append(url_pr)

        url_total_list.append(doc['url'])
        url_list_disk[doc['url']] = doc['page_links']
        new_doc = cut_word(doc)
        #print(new_doc)
        docs.append(new_doc)


    # 计算 PageRank
    digraph = nx.DiGraph()
    digraph.add_nodes_from(url_total_list)
    for url, url_list in url_list_disk.items():
        for _url in url_list:
            if _url in url_total_list:
                digraph.add_edge(url, _url)

    result = nx.pagerank(digraph, alpha=0.85)

    # 处理结果并保存到 CSV 文件
    page_rank_df = pd.Series(result, name='page_rank')
    page_rank_df = page_rank_df.apply(lambda x: math.log(x * 10000, 10) + 1)
    page_rank_df.index.name = 'url'
    #page_rank_df.to_csv("page_rank.csv", encoding='utf-8')

    # 将 PageRank 存储到每个字典中
    for doc in docs:
        url = doc['url']
        if url in page_rank_df.index:
            doc['page_rank'] = page_rank_df.loc[url]
    
    for doc in docs_clean:
        url = doc['url']
        if url in page_rank_df.index:
            doc['page_rank'] = page_rank_df.loc[url]

    for url_pr in url_prs:
        url = url_pr['url']
        if url in page_rank_df.index:
            url_pr['page_rank'] = page_rank_df.loc[url]

    save_in_csv(title_urls, 'title_url.csv', ['title', 'url', 'description', 'category'])
    save_in_csv(url_prs, 'page_rank.csv', ['url', 'page_rank'])

    fields = ['id', 'title', 'date', 'url', 'text', 'page_rank', 'description', 'news_from', 'category']
    save_in_csv(docs, 'index.csv', fields)
    save_in_csv(docs_clean, 'advanced_search_index.csv', fields)
        
    


