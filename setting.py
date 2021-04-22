# https://xmlriver.com/api/

TOP = 10
LOCS = (1011969, 1012040, 20954) #Москва, Санкт-Петербург, Новосибирск 

API_URL = 'http://xmlriver.com/search/xml?user=1660&key=9d9ea875799adf551c8329d0a6dcf50ed168f9b8'
# https://xmlriver.com/apidoc/api-about/
API_PARAMS = {
    'query':'', # текст запроса, если требуется использовать &, вместо него ставить %26
    'groupby':TOP, # Числовое значение, ТОП позиций для сбора. Возможные значения: 10, 20, 30, 50, 100;
    'loc': LOCS[0], # Москва, смотреть в файле geo.cvs
    'country': 2643, # Россия, countries.xlsx
    'lr': 'ru', # langs.xlsx
    'domain': 'com', # domains.xlsx
    'device': 'desktop', # device – устройство (desktop, tablet, mobile).
    'ads':0, # 0 - не собирает рекламу, 1 собирает
    'highlights':1 # Подсветка ключевых слов.
}

with open('query.txt', encoding='UTF-8') as f:
    base = f.readlines()
    if len(base) and base[0].find(': ') != -1:
        BASE_QUERY = dict(map(lambda f:f.replace('\n', '').split(': '), base))
    else:
        BASE_QUERY = dict(map(lambda f:(f.replace('\n', ''), None), base))