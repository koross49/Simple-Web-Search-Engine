import re
from datetime import datetime, timedelta
from app.public_const import advanced_search_index

# 高级搜索
def main_func(result, form):

    this_exact_word_or_phrase = form.this_exact_word_or_phrase.data
    any_of_these_words = form.any_of_these_words.data
    none_of_these_words = form.none_of_these_words.data
    site_or_domain = form.site_or_domain.data
    time_limit = form.time_limit.data

    text_line = advanced_search_index.loc[result[1]]
    text = f"{text_line['title']}✘{text_line['description']}✘{text_line['text']}✘{text_line['news_from']}"  # 拼合所有文本，注意用特殊字符分隔各项，避免出现奇怪的串联匹配

    # 时间限制
    if text_line['date'] != '':
        result_datetime = datetime.strptime(text_line['date'], '%Y-%m-%d %H:%M:%S')  # 时间戳转换为datetime
        if time_limit == '一天内':
            if datetime.now() - result_datetime > timedelta(days=1):
                return result
        elif time_limit == '三天内':
            if datetime.now() - result_datetime > timedelta(days=3):
                return result 
        elif time_limit == '一周内':
            if datetime.now() - result_datetime > timedelta(days=7):
                return result 
        elif time_limit == '一个月内':
            if datetime.now() - result_datetime > timedelta(days=30):
                return result 
        elif time_limit == '一年内':
            if datetime.now() - result_datetime > timedelta(days=365):
                return result 
    else:
        if time_limit != '任何时间':  # 如果没有时间戳，那么默认超过时间限制
            return result 

    # 站内匹配
    if site_or_domain:
        if site_or_domain not in result[1]:
            return result  # 如果不是指定的网站或域名，就返回这个结果方便删除，并跳出循环

    # 完全匹配
    if this_exact_word_or_phrase:
        this_exact_word_or_phrase_list = re.findall(r'\"(.+?)\"', this_exact_word_or_phrase)  # 用正则表达式提取双引号中的内容
        for word in this_exact_word_or_phrase_list:
            if word == '✘':
                pass  # 避免用于分隔的特殊字符被误判为匹配
            if word not in text:
                return result  # 如果全部文本中没有完全匹配的词，就返回这个结果方便删除，并跳出循环

    # 以下任意字词
    if any_of_these_words:
        any_of_these_words_list = any_of_these_words.split('or')  # 提取or分隔的内容
        if '' in any_of_these_words_list:
            any_of_these_words_list.remove('')  # 删除空字符串
        for word in any_of_these_words_list:
            if word == '✘':
                pass  # 避免用于分隔的特殊字符被误判为匹配
            if word in text:
                return ''  # 如果全部文本中有任意匹配的词，就跳出循环
        return result  # 如果全部文本中没有任意匹配的词，就返回这个结果方便删除，并跳出循环

    # 不含以下任意字词
    if none_of_these_words:
        none_of_these_words_list = none_of_these_words.replace('\"', '').split('-')  # 提取-分隔的内容
        if '' in none_of_these_words_list:
            none_of_these_words_list.remove('')  # 删除空字符串
        for word in none_of_these_words_list:
            if word == '✘':
                pass  # 避免用于分隔的特殊字符被误判为匹配
            if word in text:
                return result  # 如果全部文本中出现了完全匹配的词，就返回这个结果方便删除，并跳出循环

