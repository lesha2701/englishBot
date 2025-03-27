import json

def get_words_for_lessons(countWords, category=None):
    with open('./utils/words.json', 'r', encoding='utf-8') as f:
        return json.load(f)