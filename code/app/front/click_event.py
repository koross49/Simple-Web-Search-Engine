import time
import json
import csv

from flask import render_template, request, redirect, url_for, Response, jsonify

from . import front

from app.utils.search_func import main
from app.public_const import *


@front.route('/click_event', methods=['GET'])
def _click_event():
    link = request.args.get('link')
    info = url_title_df.loc[link]
    category = info['category']

    csv_file_path = './user_profile.csv'
    # 检查文件是否存在
    if not os.path.exists(csv_file_path):
        # 文件不存在，创建文件并写入列名
        with open(csv_file_path, 'w', newline='') as csv_file:
            fieldnames = ['category', 'value']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            # 写入列名
            writer.writeheader()

            
    df = pd.read_csv(csv_file_path,encoding='utf-8', index_col='category')
    if category in df.index:
        df.loc[category]['value'] += 1
        print(df.loc[category]['value'])
    else:
        new_row_data = {'value': 1}
        new_row_series = pd.Series(new_row_data, name=category)
        df.loc[category] = new_row_series

    df.to_csv(csv_file_path)

    print(link)
    return jsonify({"message": "Link received successfully"})

