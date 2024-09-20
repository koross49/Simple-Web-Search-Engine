import os
import time
import json


def save_doc(title, date, url, text, id, page_links, description, news_from, category):
    #print(title)
    doc = {
        'id': id,
        'title': title,
        'date': date,
        'url': url,
        'text': text,
        'page_links': page_links,
        'description': description,
        'news_from': news_from,
        'category': category
    }
    with open(f"data/news/{id}.json", "w") as file:
        json.dump(doc, file)

def load_doc(id):
    with open(f"data/news/{id}.json", "r") as file:
        loaded_data = json.load(file)
    return loaded_data
