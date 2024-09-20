import time
from flask import render_template, request, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired
from . import front
from app.utils.search_func import main
from app.public_const import *
from app.utils.advanced_search_func import main_func


class AdvancedSearchForm(FlaskForm):
    all_these_words = StringField('基础搜索：', validators=[DataRequired()])
    this_exact_word_or_phrase = StringField('完全匹配：')
    any_of_these_words = StringField('任意匹配：')
    none_of_these_words = StringField('排除匹配：')
    site_or_domain = StringField('站内匹配：')
    time_limit = SelectField('新闻日期', choices=["任何时间", "一天内", "三天内", "一周内", "一个月内", "一年内"], validators=[DataRequired()])
    is_title_only = RadioField('字词出现位置', choices=["网页任何位置", "仅标题"], validators=[DataRequired()])

    submit = SubmitField("高级搜索")


@front.route('/advanced_search', methods=['GET', 'POST'])
def _advanced_search():
    form = AdvancedSearchForm(is_title_only='网页任何位置')  # 默认搜索网页任何位置
    if request.method == 'GET':
        if request.args.get('keywords'):
            form.all_these_words.data = request.args.get('keywords')

    if form.validate_on_submit():
        t = time.perf_counter()  # 计时
        all_these_words = form.all_these_words.data
        #print(all_these_words)

        if request.cookies.get('search_history'):
            search_history: list = json.loads(request.cookies.get('search_history'))  # 从cookie中获取搜索历史
        else:
            search_history = []

        if form.is_title_only.data == '仅标题': 
            is_title_only = True
        else:
            is_title_only = False
        try:
            if not is_title_only:  # 搜索网页任何位置
                result_list = main(all_these_words, search_history)
            else:

                result_list = main(all_these_words, search_history, is_title_only=is_title_only)  # 搜索仅标题
            results: list[tuple] = []  

            for result in result_list:
                url = result[0]
                temp_series = url_title_df.loc[url].fillna('')
                title = temp_series['title']
                description = temp_series['description']
                cos_sim_score = result[1]
                page_rank_score = page_rank_df.loc[url]['page_rank']
                results.append((title, url, description, cos_sim_score * page_rank_score))
            # 按照cos_sim_score*page_rank_score，从大到小排序
            results.sort(key=lambda x: x[3], reverse=True)
        except KeyError:
            cost_time = f'{time.perf_counter() - t: .2f}'
            return render_template(r'no_result_page.html', keywords=all_these_words, cost_time=cost_time)

        # 第一轮基础搜索结束，开始筛选。
        del_list = []
        for result in results:
            del_list.append(main_func(result, form)) 
        results = [x for x in results if x not in del_list]  # 删除不符合条件的结果

        cost_time = f'{time.perf_counter() - t: .2f}'
        if len(results) == 0:
            return render_template(r'no_result_page.html', keywords=all_these_words, cost_time=cost_time)

        resp = Response(render_template(r'result_page.html', keywords=all_these_words, results=results, len_results=len(results), cost_time=cost_time,search_history=search_history))

        if all_these_words not in search_history:
            search_history.append(all_these_words)  # 将搜索关键词添加到历史记录中
        if len(search_history) > 12:
            search_history.pop(0)  # 如果历史记录超过12条，则删除最早的一条
        resp.set_cookie('search_history', json.dumps(search_history), max_age=60 * 60 * 24 * 30)  # 设置cookie,有效期为30天

        return resp

    return render_template(r'advanced_search.html', form=form)
