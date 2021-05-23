import json
from collections import defaultdict

import process_html
import service_cloud
import service_table
import service_webmasters
from setting import LOCS

TOP = 3
MODE_SELECTION = 1 # 0, 1
QUERY1 = 'redsale.by' # compare_url
QUERY2 = 'Наращивание ресниц 2D' # first_query

URL = 'https://redsale.by/krasota/narashivanie-resnic/2d'

def load_date(path, file_name = 'state_text'):
    try:
        with open(f'{path}\\{file_name}.json', encoding='UTF-8') as f: return json.load(f)
    except:
        return None

def get_data_search_console(url):
    r = list()
    for data in service_webmasters.get_data(url):
        r.extend(data['keys'])
    _, white_tokens = process_html.generate_tokens(' '.join(r))
    return tuple(set(white_tokens))

def data_add_word(data_result, base, data_search_console, i_col, count_default = 1):
    for word, data in base['state_words']['number_unique_words_without_stop'].items(): #_without_stop
        data_word = data_result.get(word)
        if data_word:
            data_word.update({'count':data_word['count'] + 1})
        else:
            data_word = {'count':count_default, 'GSC':'', 'i_col':list()}
            if word in data_search_console: data_word.update({'count':data_word['count'] + 1, 'GSC':'GSC'})
        if not i_col in data_word['i_col']: data_word['i_col'].append(i_col)
        if type(data) is dict:
            data_word.update({'parts_speech':data.get('parts_speech', '')})
            data_word.update({'type_entities':data['type_entities']})
        else:
            data_word.update({'parts_speech':''})
            data_word.update({'type_entities':''})
        data_result.update({word:data_word})

def process_data1(table, data_query1, data_query2, url, sheet_title, query_tokens):
    if not data_query1: data_query1 = {}
    if not data_query2: return
    print(sheet_title, ' - ', end='')
    table.select_sheet(sheet_title = sheet_title)

    title_table = [
        ['Name_block',],
        ['Compare_url_Data_con', data_query1.get('ID container')],
        ['Compare_url_Data_section', data_query1.get('ID section')],
        ['Compare_url_or_Compare_query', url],
        ['Compare_url_H1', data_query1.get('state_tags', {}).get('h', ('',))[0]],
    ]

    table.update_values(title_table, list_range = "A1:B10")
    
    if url: 
        data_search_console = get_data_search_console(url) 
    else:
        data_search_console = ()

    data_result = dict()
    if len(data_query1): data_add_word(data_result, data_query1, data_search_console, i_col = 0, count_default = 0)
    base_grams = defaultdict(int)
    for data_query0 in data_query2:
        if MODE_SELECTION == 0:
            data_selection = tuple(data_query0.values())[:TOP]
        elif MODE_SELECTION == 1:
            data_selection = list()
            for d in tuple(data_query0.values()):
                if not len(d): continue
                if len(data_selection) == TOP: break
                if query_tokens.issubset(set(process_html.generate_tokens(d["title"])[1])): # all_tokens, white_tokens
                    data_selection.append(d)

            '''
            if len(data_selection) != TOP:
                for d in tuple(data_query0.values()):
                    if len(data_selection) == TOP: break
                    for d2 in data_selection:
                        if d == d2:break
                    else:
                        data_selection.append(d2)
            '''
        for data2 in data_selection:
            data_add_word(data_result, data2, data_search_console, i_col = 1, count_default = 1)
            for word_grams in data2['state_words']['number_unique_2grams']:
                base_grams[word_grams] += 1

    data_title = ('Number_unique_words & Compare_url_or_Compare_query', 'Number_unique_words & First_query_or_First_url', 'GSC_Compare_url', 'Count_First_query_or_First_url', 'Parts_speech_First_query_or_First_url', 'Type_entities_First_query_or_First_url')
    
    data_table = []
    for name, data in data_result.items():
        data_row = ['', '', data['GSC'], data['count'], data['parts_speech'] if data.get('parts_speech') else '', data['type_entities'] if data.get('type_entities') else '']
        data_table.append(data_row)
        for i_col in data["i_col"]:
            data_row[i_col] = name
    
    indent_row = 5
    setting_cells = list()
    base_words_col_type2 = list()
    for i, t in enumerate(data_result.items()):
        if len(t[1]['i_col']) == 2:
            setting_cells.append((i + indent_row, 2))
        if 1 in t[1]['i_col']:
            base_words_col_type2.append(t[0])
        else:
            base_words_col_type2.append('')

    base_words_col_type2 = tuple(base_words_col_type2)
    base_grams = dict(sorted(base_grams.items(), key=lambda item: item[1], reverse=True))

    data_table_grams = [['', 0, '', 0, '', 0] for _ in range(len(base_words_col_type2))]
    for word, count in base_grams.items():
        words = set(word.split())
        per = words.intersection(base_words_col_type2)
        if not len(per): continue
        for check_word in per:
            i_check_word = 0
            for i_check_word, type2_word in enumerate(base_words_col_type2):
                if not check_word in type2_word.split(' '): continue
                #for ii in range
                if data_table_grams[i_check_word][1] < count: 
                    data_table_grams[i_check_word].insert(0, word)
                    data_table_grams[i_check_word].insert(1, count)
                elif data_table_grams[i_check_word][3] < count: 
                    data_table_grams[i_check_word].insert(2, word)
                    data_table_grams[i_check_word].insert(3, count)
                elif data_table_grams[i_check_word][5] < count: 
                    data_table_grams[i_check_word].insert(4, word)
                    data_table_grams[i_check_word].insert(5, count)
                data_table_grams[i_check_word] = data_table_grams[i_check_word][:6]

    data_table_grams.insert(0, ('Number_unique_2grams_1_First_query_or_First_url', 'count.n-gram1', 'Number_unique_2grams_2_First_query_or_First_url', 'count.n-gram2', 'Number_unique_2grams_3_First_query_or_First_url', 'count.n-gram3'))

    data_sum = [0, 0, 0, '', '', 0]
    for data_row in data_result.values():
        if len(data_row['i_col']) == 1:
            data_sum[data_row['i_col'][0]] += 1
        if data_row['GSC'] != "":
            data_sum[2] += 1
        if data_row['type_entities'] and data_row['type_entities'] != "":
            data_sum[5] += 1
    
    data_table.insert(0, data_sum)
    data_table.insert(1, data_title)
    step = 500
    i_step2 = indent_row
    for i_step in range(0, len(data_table) + 1, step):
        b = data_table[i_step:i_step + step]
        b.append(['',])
        print(i_step2)
        tt =  f'C{i_step2}:i{i_step2 + len(b) + 1}'
        print(tt)
        table.update_values(b, list_range = tt)
        i_step2 = i_step2 + len(b) - 1
        ii = 0
     # C3I3!!!
    #table.update_values(data_table, list_range = f'C4:I{len(data_result) + indent_row}') # C3I3!!!
    i_step2 = indent_row + 1
    for i_step in range(0, len(data_table_grams) + 1, step):
        b = data_table_grams[i_step:i_step + step]
        b.append(['',])
        table.update_values(b, list_range = f'J{i_step2}:Q{i_step2 + len(b)}')
        i_step2 = i_step2 + len(b) - 1
        ii = 0
     # C3I3!!!
    table.set_format_Cell(setting_cells)
    print('ok', flush=True)

def process_data2(table, data_result, data_query1, data_query2, sheet_title):
    def cals_state(table_row, item):
        table_row[1] += item['state_words']['number_characters']
        table_row[2] += item['state_words']['number_all_words']
        table_row[3] += item['state_words']['number_all_words_without_stop']
        table_row[4] += item['state_words']['number_all_unique_words']
        table_row[5] += item['state_words']['number_all_unique_words_without_stop']
        table_row[6] += 0 # количество Type entities

        table_row[7] += len(item['state_tags']['h'])
        table_row[8] += item['state_tags']['table_count']
        table_row[9] += item['state_tags']['img_count']
        table_row[10] += len(item['state_tags']['schema_type'])
        table_row[11] += 1 if item.get('fag_rich_snippet') else 0
        table_row[12] += 1 if item.get('oneline_sitelinks') else 0
        #print(item.get('extended_passage'))
        table_row[13] +=  1 if item.get('extended_passage') else 0
    table.select_sheet(sheet_title = f'{sheet_title}_2')
    table_titles = ['query', 'number_characters', 'number_all_words', 'number_all_words_without_stop', 'number_all_unique_words', 'number_all_unique_words_without_stop', 'Type entities', 'h_count', 'table_count', 'img_count', 'schema_type_count', 'fag_rich_snippet', 'oneline_sitelinks', 'extended_passage']#list()
    #for title in ['query', 'number_characters', 'number_all_words', 'number_all_words_without_stop', 'number_all_unique_words', 'number_all_unique_words_without_stop', 'Type entities', 'h_count', 'table_count', 'img_count', 'schema_type_count', 'fag_rich_snippet', 'oneline_sitelinks', 'extended_passage']:
    #    table_titles.append((title,))


    table.update_values((table_titles,), list_range = f'A1:O2')
    table_result = list()
    title = ['TOP 1-3',
            'TOP 4-10',
            'TOP 11 - 20',
            'Compare_url_or_Compare_query'
    ]
    for i_start, count in [(0, 3), (3, 10), (10, 20)]:
        table_row = list()
        table_result.append(table_row)
        table_row.append(title.pop(0))
        for _ in range(13): table_row.append(0)
        for i, data_query0 in enumerate(data_query2):
            for item1, item2 in tuple(zip(data_result[i]["items"], data_query0.items()))[i_start:count]:
                url, item3 = item2
                cals_state(table_row, item3)
        for i_col in range(1, 11): table_row[i_col] = round(table_row[i_col] / (count - i_start))
    table_row = list()
    table_result.append(table_row)
    table_row.append(title.pop(0))
    for _ in range(13): table_row.append(0)
    cals_state(table_row, data_query1)

            #print(item1, item2)

    table.update_values(table_result, list_range = f'A2:O{len(table_result) + 1}')

from setting import BASE_QUERY

def get_currect_table(base_table, count_max = 50):
    for table, count in base_table.items():
        if count < count_max: 
            base_table.update({table:count + 1})
            return table
    raise Exception('Подходящие таблицы кончились!')

def process_metric():
    table_ids = ('1utinFVgu39rsTpZRKim5lsqtquFRdsFG2EXYQFyC5hg', '1b5iLmSZJBmxmjT-EYCxXf4TUdRM0qB6BkuM0GczRS2U', '1alZ1WT_aB9q25gU583VF365JtExhxTzX3UM9C4b3mlQ', '1Ev16Q50Sa8i-zUhuO7XvTvTiuJ6SZN9DdFjfeNp12-Y', '1M2knu0DHyXUuLVogW9tzHi0DLRmemU4cIoQd2yboV3U', '1PWQvwiUD7ErWmp0lRYV9KH-zp1IBD2mMMeSok7mzhRM')
    base_table = dict()
    sheet_names = list()
    print('check tables')
    for table_id in table_ids:
        table = service_table.Table(table_id)
        print('очищаем таблицу', table.table_title)
        table.delete_sheet_all()
        base_table.update({table:len(table.sheet_list)})
        sheet_names.extend(table.sheet_list)
    print('process metric')
    #print(base_table)
    base_info = BASE_QUERY 
    
    for sheet_title, url in base_info.items():
        if sheet_title in sheet_names: continue
        try:
            data_query1 = load_date('data_metrics').get(url)
        except:
            data_query1 = None
        data_query2 = list()
        data_result = list()
        for loc_name in LOCS:
            data_query2.append(load_date(f'data\\{loc_name}\\{sheet_title}'))
            data_result.append(load_date(f'data\\{loc_name}\\{sheet_title}', 'result'))
        query_tokens = []
        if MODE_SELECTION == 1: query_tokens = set(process_html.generate_tokens(sheet_title)[1]) # all_tokens, white_tokens
        table = get_currect_table(base_table)
        process_data1(table, data_query1, data_query2, url, sheet_title, query_tokens = query_tokens)
        #process_data2(table, data_result, data_query1, data_query2, sheet_title)

def generate_tables(base_parsing_tables, table_id = '1utinFVgu39rsTpZRKim5lsqtquFRdsFG2EXYQFyC5hg'):
    table = service_table.Table(table_id)
    table.select_sheet('0')
    table.update_values(base_parsing_tables, list_range = None)

if __name__ == '__main__':
    process_metric()
    