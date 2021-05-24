import traceback

import api_xmlriver
import metrics
import process_html
from setting import BASE_QUERY, LOCS

# 0 - выключение, 1 - включение!
#################################
XML_MODE = 1 # парсинг с xmlriver
HTML_MODE = 1 # парсинг html по url полученным с xmlriver, используется chrome
TABLE_MODE = 1 # генерирование таблиц с сохраннённых html страниц
METRIC_MODE = 1 # генерирование метрик лист = данные по query
#################################
def main(): 
    b = process_html.Browser()
    b.set_show()
    b.run()
    base_tables = BASE_QUERY
    for q, url in base_tables.items(): 
        if url: process_html.start_process_url(url, b)
    
    for loc in LOCS:
        for q, url in base_tables.items():
            path = f'data\\{loc}\\{q}'  
            if XML_MODE:
                api_xmlriver.generation(path, q, loc)
                api_xmlriver.process(path)
            if HTML_MODE:
                b = process_html.parsers(path, b)
                process_html.start_process(path)
                
    if TABLE_MODE:
        base_parsing_tables = list()
        for loc in LOCS:
            for q, url in base_tables.items():
                path = f'data\\{loc}\\{q}'  
                base_parsing_tables.append((q, '', '', '', ''))
                process_html.process_table(path, base_parsing_tables)
        metrics.generate_tables(base_parsing_tables)

    if METRIC_MODE:
        metrics.process_metric() # генерирует таблицы метрик
    

if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc() 
    input('Процесс завершён.')
