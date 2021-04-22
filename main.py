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
    for loc in LOCS:
        for q, url in base_tables.items():
            path = f'data\\{loc}\\{q}'  
            print(path)
            api_xmlriver.generation(path, q, loc)
            api_xmlriver.process(path)
            b = process_html.parsers(path, b)
            process_html.start_process(path)
    metrics.process_metric() # генерирует таблицы метрик

if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
    input('Процесс завершён.')
