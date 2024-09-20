from bs4 import BeautifulSoup
import urllib.request
from datetime import timedelta, date
import time
import urllib.parse
import os
import requests
from util import save_doc
import re

headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58",
        "Connection":"keep-alive",
        #指定此次请求来源
        "Referer":
            "https://www.chinanews.com.cn"
}

keyword='编辑'

# 获取一页新闻的函数
def get_one_page_news(page_url):

    # 处理响应
    print(page_url)
    response = requests.get(url=page_url, headers=headers)
    status_code = response.status_code
    if status_code == 200:
        html = response.text
    soup = BeautifulSoup(html,"html.parser",from_encoding='gbk')
    
    news_pool = []
    news_list = soup.find('div', class_ = "content_list")
    items = news_list.find_all('li')

    for i,item in enumerate(items):
        if len(item) == 0:
            continue
        
        a = item.find('div', class_ = "dd_bt").find('a')
        title = a.string
        url = a.get('href')
        
        category = ''
        try:
            category = item.find('div', class_ = "dd_lm").find('a').string
        except Exception:
            continue
        
        if category == '图片':
            continue
        
        year = url.split('/')[-3]
        date_time = item.find('div', class_ = "dd_time").string
        date_time = '%s-%s:00'%(year, date_time)
        
        news_info = [date_time, "http://www.chinanews.com"+url, title]
        news_pool.append(news_info)
    return news_pool

# 获取新闻池的函数
def get_news_pool(start_date, end_date):
    news_pool=[]
    delta = timedelta(days=1)
    while start_date <= end_date:
        date_str=start_date.strftime("%Y/%m%d")
        page_url='http://www.chinanews.com/scroll-news/%s/news.shtml'%(date_str)
        news_pool += get_one_page_news(page_url)
        start_date += delta
    return news_pool

# 爬取新闻的函数
def crawl_news(news_pool, min_body_len):
    i = 1
    for n, news in enumerate(news_pool):
        print('%d/%d'%(n,len(news_pool)))
        
        req = urllib.request.Request(news[1], headers = headers)
        try:
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read()
        except Exception:
            continue
        
        soup = BeautifulSoup(html, "html.parser")
        [s.extract() for s in soup('script')]
        
        try: # 新闻正文
            ps = soup.find('div', class_ = "left_zw").find_all('p')
        except Exception:
            continue
        
        try: # 新闻标题
            t = soup.find('h1', class_ = "content_left_title")
        except Exception:
            continue
        title = t.string

        try: # 指向其他页面的链接，为后续page_rank做准备
            links = soup.find_all('div', class_ = "intermoren_left")
        except Exception:
            continue
        
        page_links = []
        for link in links:
            tem = link.find('a')
            link_str = "http://www.chinanews.com"+tem.get('href')
            page_links.append(link_str)

        try: # 获取新闻来源
            news_info = soup.find('div', class_ = "content_left_time").contents[0].strip()
        except Exception:
            continue

        info_str = news_info
        index_of_source = info_str.find("来源：")
        if index_of_source != -1:
            news_from = info_str[index_of_source + len("来源："):]
        else:
            news_from = '中国新闻网'
        
        if not news_from: # 如果未注明新闻来源，默认为中国新闻网
            news_from = '中国新闻网'
        
        body = ''
        for p in ps:
            cur = p.get_text().strip()
            if cur == '':
                continue
            body += '\t' + cur + '\n'
        body = body.replace(" ", "")

        description = body.split('\n', 1)[0].replace("\t", "").replace("\n", "")
        
        category = re.search(r'http://www\.chinanews\.com/(.*?)/', news[1]).group(1) # 新闻种类位于链接中
        save_doc(title, news[0], news[1], body, i, page_links, description, news_from, category)

        with open(f"data/htmls/{i}.html", "wb") as file:
            file.write(html)

        i += 1
        time.sleep(1)
    
if __name__ == '__main__':

    # 指定文件夹路径
    folder_path = 'data/news/'
    # 创建文件夹（如果不存在）
    os.makedirs(folder_path, exist_ok=True)

    folder_html_path = 'data/htmls/'
    # 创建文件夹（如果不存在）
    os.makedirs(folder_html_path, exist_ok=True)

    # 获取近5日新闻
    end_date = date.today()
    start_date = end_date + timedelta(days=-5)

    news_pool = get_news_pool(start_date, end_date)
    print('start scraping')
    crawl_news(news_pool, 140)
    print('over')
