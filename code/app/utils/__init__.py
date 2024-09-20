import re

# 模糊查找
def input_fuzzy_finder(input_word, words_list):
    suggestions = []
    regex = re.compile('.*?'.join(input_word))  # 完成正则表达式的创建
    for word in words_list:
        match = regex.search(word)  # 通过正则表达式进行匹配
        if match:
            suggestions.append((len(match.group()), match.start(), word))
    return [x for _, _, x in sorted(suggestions)]
