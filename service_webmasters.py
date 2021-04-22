import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import datetime
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly',]

def get_data(url = 'https://redsale.by/krasota/narashivanie-resnic'):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())

    service = build('webmasters', 'v3', credentials=creds)

    request = {
        'startDate': '2021-03-10',
        'endDate': datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d'),
        'dimensions': ['query'],
        "searchType": "web",
        "dimensionFilterGroups": [
                {
                    "filters": [
                        {
                            "dimension": "page",
                            "operator": "contains",
                            "expression": url
                        }
                    ]
                }
            ],
    }
    return tuple(service.searchanalytics().query(siteUrl="https://redsale.by", body=request).execute().get('rows', ()))



if __name__ == '__main__':
    get_data()
    