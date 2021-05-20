import traceback

import api_xmlriver
import metrics
import process_html
from setting import BASE_QUERY, LOCS

def main(): 
    b = process_html.Browser()
    b.set_show()
    b.run()
    base_tables = BASE_QUERY
    for q, url in base_tables.items(): 
        if url: process_html.start_process_url(url, b)
    base_parsing_tables = list()
    for loc in LOCS:
        i = 0
        for q, url in base_tables.items():
            path = f'data\\{loc}\\{q}'  
            print(path)
            api_xmlriver.generation(path, q, loc)
            api_xmlriver.process(path)
            b = process_html.parsers(path, b)
            base_parsing_tables.append((q, '', '', '', ''))
            process_html.start_process(path, base_parsing_tables)
    metrics.process_metric() # генерирует таблицы метрик
    metrics.generate_tables(base_parsing_tables)

if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc() 
    input('Процесс завершён.')
