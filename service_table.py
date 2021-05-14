# установка
# 1) pip3 install --upgrade google-api-python-client
# 2) pip3 install oauth2client

# адрес сервисного аккаунта ts-234@task-8-308209.iam.gserviceaccount.com
# гайд https://habr.com/ru/post/483302/


import os.path
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1utinFVgu39rsTpZRKim5lsqtquFRdsFG2EXYQFyC5hg'

class Table:
    def __init__(self, spreadsheetId = None, table_title = 'Новая таблица'):
        self.service = self.get_service()
        self.table_title = table_title
        if spreadsheetId is None:spreadsheetId = self.create_table(table_title = table_title)
        self.spreadsheetId = spreadsheetId
        self.sheet_list = self.get_sheets()
        #print(self.sheet_list)
        
    def select_sheet(self, sheet_title):
        self.sheet_title = sheet_title
        self.sheetId = self.sheet_list.get(sheet_title)
        if self.sheetId is None: self.sheetId = self.create_sheet(sheet_title)

    def get_service(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return build('sheets', 'v4', credentials=creds)
    
    def get_table_info(self):
        request = self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId, ranges=[], includeGridData=False)
        return request.execute()

    def get_sheets(self):
        sheet_list = dict()
        for sheet in  self.get_table_info()['sheets']:
            properties = sheet['properties']
            sheet_list.update({properties['title']:properties['sheetId']})
        return sheet_list

    def create_table(self, table_title):
        spreadsheet = self.service.spreadsheets().create(body = {
            'properties': {'title': table_title, 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                    'sheetId': 0,
                                    'title': 'Новый лист',
                                    'gridProperties': {'rowCount': 1, 'columnCount': 1}}}]
        }).execute()
        spreadsheetId = spreadsheet['spreadsheetId']
        print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)
        return spreadsheetId# сохраняем идентификатор файла
    
    def create_sheet(self, sheet_title):
        if sheet_title in self.sheet_list.keys(): return False
        results = self.service.spreadsheets().batchUpdate(
        spreadsheetId = self.spreadsheetId,
        body = {
            "requests": [
                {
                "addSheet": {
                    "properties": {
                    "title": sheet_title,
                    "gridProperties": {
                        "rowCount": 100,
                        "columnCount": 30
                    }
                    }
                }
                }
            ]
            }).execute() #'replies': [{'addSheet': {'properties': {'sheetId
        return results['replies'][0]['addSheet']['properties']['sheetId']

    def delete_sheet(self):
        body = {
            'requests': [
                    {"deleteSheet": {"sheetId": self.sheetId}}
            ]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheetId,
            body=body).execute()

    def delete_sheet_all(self):
        self.create_sheet('0')
        for sheet_title in self.sheet_list.keys():
            if sheet_title == '0': continue
            self.select_sheet(sheet_title)
            print('удаляем лист:', sheet_title)
            self.delete_sheet()
            time.sleep(1)

    def update_values(self, data, list_range = "B2:D5"):
        print(list_range)
        self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = {
            "valueInputOption": "USER_ENTERED", # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {
                    "range": f'{self.sheet_title}!{list_range}', 
                    "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                    "values": data
                }
            ]
        }).execute()
    
    def set_size_colomn(self):
        self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = {
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": self.sheetId,
                        "dimension": "COLUMNS",  # Задаем ширину колонки
                        "startIndex": 0, # Нумерация начинается с нуля
                        "endIndex": 2 # Со столбца номер startIndex по endIndex - 1 (endIndex не входит!)
                        },
                        "properties": {
                        "pixelSize": 250 # Ширина в пикселях
                        },
                        "fields": "pixelSize" # Указываем, что нужно использовать параметр pixelSize  
                    }
                },
            ]}
        ).execute()
    
    def set_format_Cell(self, cells):
        if not len(cells): return
        requests = list()
        for cell in cells:
            setting_cell = {
                "repeatCell": 
                {
                    "cell": 
                    {
                    "userEnteredFormat": 
                    {
                        "backgroundColor": {
                            "red": 0.2,
                            "green": 0.7,
                            "blue": 0.2,
                            "alpha": 1
                        },
                    }
                    },
                    "range":{
                        "sheetId": self.sheetId,
                        "startRowIndex": cell[0],
                        "endRowIndex": cell[0] + 1,
                        "startColumnIndex": cell[1],
                        "endColumnIndex": cell[1] + 2
                    },
                    "fields": "userEnteredFormat"
                }
            }
            requests.append(setting_cell)
        self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = {"requests": requests}).execute()


if __name__ == '__main__':
    table = Table(table_title = 'Metric6') #main() №'1utinFVgu39rsTpZRKim5lsqtquFRdsFG2EXYQFyC5hg'
    
