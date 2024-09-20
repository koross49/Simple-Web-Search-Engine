import json
import csv

from flask import render_template, request, jsonify
from app.utils.search_func import main
from app.public_const import *
from . import front

def get_user_profile(csv_file_path):
    # 读取CSV文件
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        # 跳过第一行（列名）
        next(reader, None)
        # 读取第一列，获取种类
        categories = []
        # 读取第二列，获取得分
        scores = []
        for row in reader:
            categories.append(row[0])
            scores.append(float(row[1]))
        # 计算总分
        total_score = sum(scores)
        # 计算每个种类得分在总分中的占比
        percentages = [score / total_score for score in scores]
        # 将种类和对应占比组成字典
        result = dict(zip(categories, percentages))
    return result

def calculate_ratio(result_list):
    total_second_values = sum(value for _, value in result_list)
    new_result_list = [(key, value / total_second_values) for key, value in result_list]
    return new_result_list

def get_url_list(category, num):
    specific_value_rows = url_title_df1[url_title_df1['category'] == category]
    tt=specific_value_rows.sample(n=num)
    result_dict_list = tt[['title', 'url']].to_dict(orient='records')
    return result_dict_list


@front.route('/suggest', methods=['GET'])
def _suggest():

    keywords = request.args.get('keywords')
    if not keywords:
        ret_list = []
        return jsonify(ret_list)
    #print(keywords)

    up = get_user_profile('./user_profile.csv')

    search_history = []

    try:
        result_list: list[tuple[str, float]] = main(keywords, search_history,True)
        print(result_list)
    except KeyError :
        try:
            result_list: list[tuple[str, float]] = main(keywords, search_history,False)
            print(result_list)
        except KeyError:
            result_list = []
    
    sug_url_list = []

    if not result_list:
        nums = 6
        for category, percentage in up.items():
            temp_list = get_url_list(category, percentage*nums)
            sug_url_list.extend(temp_list)
    else:
        temp_list = []
        res_list = calculate_ratio(result_list)
        for item in res_list:
            url = item[0]
            sc_1 = item[1]
            cate = (url_title_df.loc[url])['category']
            title = (url_title_df.loc[url])['title']
            if cate in up:
                sc_2 = up[cate]
            else:
                sc_2 = 0
            sc = 2*sc_1 + sc_2
            temp_list.append({
                'title':title,
                'url':url,
                'score':sc
            })
        sorted_temp_list = sorted(temp_list, key=lambda x: x['score'], reverse=True)
        sug_url_list = [{k: v for k, v in d.items() if k != 'score'} for d in sorted_temp_list[:6]]


    ret_list = []
    for item in sug_url_list:
        _url = item['url']
        _title = item['title']
        sug = f'<a href="{_url}">{_title}</a>'
        ret_list.append(sug)

    return jsonify(ret_list)



