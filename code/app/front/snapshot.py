import json

from flask import render_template, request

from . import front
from app.public_const import *


@front.route('/snapshot')
def _snapshot():
    if url := request.args.get('url'):
        title = url_title_df.loc[url]['title']
        id = advanced_search_index.loc[url]['id']
        with open(rf'./data/htmls/{id}.html',encoding='utf-8') as f:
            snapshot = f.read()
        # 以网页的形式返回快照
        return render_template(r'snapshot.html', snapshot=snapshot)
    else:
        return "不合法的参数"
