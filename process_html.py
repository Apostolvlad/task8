import json
import os
import re
import traceback
from collections import defaultdict

import nltk 
import pandas as pd
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.util import ngrams
from pymorphy2 import MorphAnalyzer

import service_cloud
from browser import Browser

nltk.download('stopwords')
morph = MorphAnalyzer()
# pip install pymorphy2
# pip install nltk

def parsers(path, b = None):
    base_path = f'{path}\\base'
    if os.path.exists(base_path):
        return b
        for p in os.listdir(base_path):
            os.remove(f'{base_path}\\{p}')
    else:
        os.mkdir(base_path)
    with open(f'{path}\\result.json', encoding='UTF-8') as f: base = json.load(f)
    if b is None:
        b = Browser()
        b.set_show()
        b.run()
    for item in base.get('items'):
        html = ''
        for i in range(3):
            try:
                b.get(item['url'])
                html = b.driver.page_source
                break
            except Exception as e:
                print(e)
                b = Browser()
                b.set_show()
                b.run()
        with open(f'{base_path}\\pos_{item["position"]}.html', 'w', encoding='UTF-8') as f: f.write(html)
    return b

def parser_url(url, b = None):
    if b is None:
        b = Browser()
        b.run()
    b.get(url)
    #with open(f'data_metrics\\data_url.html', 'w', encoding='UTF-8') as f: f.write(b.driver.page_source) #
    return b.driver.page_source

def get_tag_elements(soup, name):
    reg1 = re.compile('[^а-яА-Я0-9 ]')
    reg2 = re.compile('\s+')
    result = list()
    for tag in soup.find_all(name):
        if name == 'img':
            if not tag.get('alt'): continue
            result.append(reg2.sub(' ', reg1.sub(' ', tag.get('alt'))))
        else:
            if tag.text in ['', "\n\n"]: continue
            result.append(reg2.sub(' ', reg1.sub(' ', tag.text)))
    return result

def get_schema_type(contents, result):
    contents = contents.replace(' ', '').replace('\n', '')
    
    schema_type = list()
    i_context = 0
    while 1:
        i_context += 1
        i_context = contents.find('schema.org","@type"', i_context)
        if i_context == -1: break
        i_type = contents.find('"@type"', i_context)
        if i_type == -1: continue
        i_type += 9
        schema_type.append(contents[i_type:contents.find('"', i_type)])
        
    result['state_tags'].update({'schema_type':schema_type})


def process_tags(soup, result):
    print('process tag - ', end = '')
    result2 = dict()
    body = soup.find('body')
    hh = list()
    for i in range(1, 5): hh.extend(get_tag_elements(body, f'h{i}'))
    result2.update({'h':hh}) 
    result2.update({'a':get_tag_elements(body, 'a')})
    result2.update({'img_alt':get_tag_elements(body, 'img')})
    result2.update({'img_count':len(body.find_all('img'))})
    result2.update({'table_count':len(body.find_all('table'))})
    result.update({'state_tags':result2})

def check_word_freq(tokens):
    word_freq = defaultdict(int)
    all_count_list = 0
    for token in tokens:
        if token.replace(' ', '').isdigit(): continue
        word_freq[token] += 1
        all_count_list += 1
    return word_freq, all_count_list

def check_word_frequency(data_unique_words, all_count):
    word_state = defaultdict(float)
    for token, count in data_unique_words.items():
        word_state[token] = round(count / all_count * 100, 4)
    return word_state

def generate_ngrams(parts, n):
    stopwords_ru = stopwords.words("russian")
    base_ngrams = list()
    for p in parts:
        words = list()
        for word in p.split():
            word = word.strip()
            word = morph.normal_forms(word)[0]
            if not word or word in stopwords_ru: continue
            words.append(word)
        base_ngrams.extend(ngrams(words, n))
    #base_ngrams = list(ngrams(set(tokens), n))#zip(*[tokens[:i] for i in range(n)])
    return [" ".join(ngram) for ngram in base_ngrams]

def text_split_parts(text):
    text = text.replace(' .', '.').replace('. ', '\n')
    text_parts = list()
    for t in text.splitlines():
        t = t.strip()
        if t == '': continue
        if t.find(' ') == -1 or t.replace(' ', '').isdigit(): continue
        text_parts.append(t)
    return text_parts

def delete_digit(base):
    for item in base:
        pass

def generate_tokens(text):
    stopwords_ru = stopwords.words("russian")
    all_tokens = []
    white_tokens = []
    for token in text.split():
        token = token.strip().replace('.', '')
        token = morph.normal_forms(token)[0]
        if not token: continue
        all_tokens.append(token)
        if token in stopwords_ru: continue
        white_tokens.append(token)
    return all_tokens, white_tokens

def process_context(soup, result):
    print('process content - ', end = '')
    text = soup.find('body').get_text()
    reg1 = re.compile('[^а-яА-Яa-zA-Zё0-9. \n]')
    reg2 = re.compile(' +')
    text = reg2.sub(' ', reg1.sub(' ', text))#reg1.sub(' ', text)#reg2.sub(' ', reg1.sub(' ', text))
    if soup.title: 
        title = soup.title.text
    else:
        title = ''

    description = soup.find('meta', {'name':'description'})
    if description: 
        description = description.get('content')
    else:
        description = ''

    result.update({'title':title, 'description':description})
    data_section = soup.find('a', class_ = 'js-popup-open button big invert w250')
    data_con = soup.find('div', class_ = 'org-heading-right')
    if data_section and data_con:result.update({'ID section':data_section.get('data-section'), 'ID container':data_con.get('data-con')})
    #with open('text_test.txt', 'w', encoding='UTF-8') as f:
    #    f.write('\n'.join(r))


    #with open('stopwords_ru.txt', 'w', encoding='UTF-8') as f:
    #   f.write('\n'.join(stopwords_ru))

    all_tokens, white_tokens = generate_tokens(text)

    text_parts = text_split_parts(text)
    base_2grams = generate_ngrams(text_parts, 2)

    number_unique_words, _ = check_word_freq(all_tokens)
    number_unique_words_without_stop, _ = check_word_freq(white_tokens)
    
    number_unique_2grams, list_all_2grams = check_word_freq(base_2grams)

    relative_frequency_all_words = check_word_frequency(number_unique_words, len(all_tokens))
    relative_frequency_all_words_without_stop = check_word_frequency(number_unique_words_without_stop, len(white_tokens))

    for key, data_word in number_unique_words_without_stop.items():
        number_unique_words_without_stop.update({key:{'type_entities': '', 'parts_speech':'', 'count':data_word}})

    state_words = dict()
    state_words.update({'number_characters': len(text)})
    state_words.update({'number_all_words': len(all_tokens)})
    state_words.update({'number_all_words_without_stop': len(white_tokens)})
    state_words.update({'number_all_unique_words': len(number_unique_words)})
    state_words.update({'number_all_unique_words_without_stop': len(number_unique_words_without_stop)})

    state_words.update({'number_all_2grams': len(base_2grams)})
    state_words.update({'list_all_2grams':list_all_2grams})
    state_words.update({'number_all_unique_2grams': len(number_unique_2grams)})
    
    
    #state_words.update({'number_all_relative_frequency': len(relative_frequency_all_words)})
    #state_words.update({'number_all_relative_frequency_without_stop': len(relative_frequency_all_words_without_stop)})

    state_words.update({'number_unique_words': len(number_unique_words)})
    state_words.update({'number_unique_words_without_stop': len(number_unique_words_without_stop)})
    state_words.update({'number_unique_2grams': len(number_unique_2grams)})

    state_words.update({'number_unique_words': number_unique_words})
    state_words.update({'number_unique_words_without_stop': number_unique_words_without_stop})
    state_words.update({'number_unique_2grams': number_unique_2grams})

    state_words.update({'relative_frequency_all_words': relative_frequency_all_words})
    state_words.update({'relative_frequency_all_words_without_stop': relative_frequency_all_words_without_stop})



    result.update({'state_words':state_words})

    #with open('test_text.txt', 'w', encoding='UTF-8') as f:
    #    f.write(text)

def analyze_entities(result):
    print('analyze entities - ', end = '')
    base_words = list(filter(lambda x: set(x).isdisjoint(('1','2','3','4','5','6','7','8','9','0')), result['state_words']['number_unique_words_without_stop'].keys()))
    base_entities = service_cloud.analyze_entities('\n'.join(base_words))
    for entities in base_entities:
        result['state_words']['number_unique_words_without_stop'][entities['name']].update({'type_entities': entities['type']})
        #result['state_words']['number_unique_words_without_stop'].update({entities['name']:{'type_entities': entities['type'],'count':result['state_words']['number_unique_words_without_stop'].get(entities['name'])}})

#https://pymorphy2.readthedocs.io/en/0.2/user/index.html
def analyze_parts_speech(result):
    print('analyze parts speech - ', end = '')
    base_words = list(filter(lambda x: set(x).isdisjoint(('1','2','3','4','5','6','7','8','9','0')), result['state_words']['number_unique_words_without_stop'].keys()))
    for data_word in base_words:
        result['state_words']['number_unique_words_without_stop'][data_word].update({'parts_speech': morph.parse(data_word)[0].tag.POS})
    
def start_process_url(url, b):
    if not os.path.exists('data_metrics'): os.mkdir('data_metrics')
    if os.path.exists('data_metrics\\state_text.json'):
        with open(f'data_metrics\\state_text.json', encoding='UTF-8') as f: base = json.load(f)
    else:
        base = dict()
    result = dict()
    if base.get(url): return False
    base.update({url:result})
    process(parser_url(url, b), result)
    with open(f'data_metrics\\state_text.json', "w", encoding='UTF-8') as f:
        f.write(json.dumps(base, indent=4, ensure_ascii=False))

def process(contents, result):
    soup = BeautifulSoup(contents, 'lxml')
    
    process_tags(soup, result)
    get_schema_type(contents, result)
    process_context(soup, result)
    analyze_parts_speech(result)
    #analyze_entities(result)
    print('OK!')
    
def start_process(path):
    if os.path.exists(f'{path}\\state_text.json'): return True
    with open(f'{path}\\result.json', encoding='UTF-8') as f: urls = json.load(f)['items']
    print('start process base - ', end = '')
    base = dict()
    for url, element in zip(urls, os.listdir(f'{path}\\base')):
        #print(element)
        result = dict()
        base.update({url['url']:result})
        if element.find('html') == -1:continue
        with open(f'{path}\\base\\{element}', encoding='UTF-8') as f: contents = f.read()
        try:
            process(contents, result)
        except:
            print('not OK!')
            print(url)
            traceback.print_exc()
            continue
        print('process html -', end = '')
    print('finish')
    with open(f'{path}\\state_text.json', "w", encoding='UTF-8') as f:
        f.write(json.dumps(base, indent=4, ensure_ascii=False))
    print('saved!')
    
        








if __name__ == '__main__':
    process_tags()
    