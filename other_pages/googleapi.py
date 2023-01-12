from __future__ import print_function

# google api related imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# streamlit secret
import streamlit as st

# ========================= Some constants
# sheets
sheets_dict = st.secrets['database']
db_primary = sheets_dict['base']
db_sadhana_card = sheets_dict['sadhana_card']
db_list = {1:db_primary,
            2:db_sadhana_card
            }
# credentials
creds = Credentials.from_authorized_user_info(st.secrets['refresh_token'])
# ========================= Some constants end


def download_data(db_id,range_name,major_dimention='ROWS'):
    """
    * for sheet choose value from
    1. database
    2. sadhana card
    """    
    if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheetID = db_list[db_id]
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetID,
            range=range_name,
            majorDimension=major_dimention
            ).execute()

        values = result.get('values', [])
        return values
    except HttpError as err:
        st.write(err)
        # pass

def upload_data(db_id,range_name,value,input_type='RAW'):
    """
    * for sheet choose value from
    1. database
    2. sadhana card    
    """
    if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        body = {
            'values': value
        }
        spreadsheetID = db_list[db_id]
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheetID, range=range_name,
            valueInputOption=input_type, body=body,
            includeValuesInResponse=True
            ).execute()
        
        return result['updatedData']
    except HttpError as err:
        # st.write(err)
        pass


def append_data(db_id,range_name,value,input_type='RAW'):
    """
    * for sheet choose value from
    1. database
    2. sadhana card    
    """
    if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        body = {
            'values': value
        }
        spreadsheetID = db_list[db_id]
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheetID, range=range_name,
            valueInputOption=input_type, body=body,
            insertDataOption = 'INSERT_ROWS',
            includeValuesInResponse=True
            ).execute()
        
        return result['updates']
    except HttpError as err:
        # st.write(err)
        pass

# def _append_range(spreadsheet_id,range_name,value):
#     if creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#     try:
#         service = build('sheets', 'v4', credentials=creds)

#         # Call the Sheets API
#         body = {
#             'values': value
#         }
#         result = service.spreadsheets().values().append(
#             spreadsheetId=spreadsheet_id, range=range_name,
#             valueInputOption='RAW', body=body,
#             includeValuesInResponse=True).execute()

#         values = result.get('values', [])
#         return value
#         # return pd.DataFrame(values[1:],columns=values[0])
#     except HttpError as err:
#         st.write(err)
