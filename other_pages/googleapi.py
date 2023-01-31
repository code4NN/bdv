import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
credentials_info = st.secrets['service_account']
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]
# ========================= Some constants end
def _get_wb(db_id):
    if f'spreadsheet{db_id}' not in st.session_state:
            gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(credentials_info,SCOPE))
            workbook = gc.open_by_key(db_list[db_id])
            st.session_state[f'spreadsheet{db_id}'] = workbook
            # workbook.worksheet('jai').update(values=[[]],range_name='',raw=False)

    return st.session_state[f'spreadsheet{db_id}']

def download_data(db_id,range_name):
    """
    * for sheet choose value from
    1. database
    2. sadhana card
    """
    try:            
        workbook = _get_wb(db_id)
        sheetname, rangename = range_name.split("!")
        response = workbook.worksheet(sheetname).get_values(rangename)        
        return response
    except Exception as e:
        st.write(e)

def upload_data(db_id,range_name,value):
#     """
#     * for sheet choose value from
#     1. database
#     2. sadhana card    
#     """
    try:
        workbook = _get_wb(db_id)
        sheetname, rangename = range_name.split("!")
        response = workbook.worksheet(sheetname).update(rangename,
                                    value,
                                    value_input_option='USER_ENTERED')
        return response
    except Exception as e:
        st.write(e)



def append_data(db_id,range_name,value):
#     """
#     * for sheet choose value from
#     1. database
#     2. sadhana card    
#     """
    try :
        wb = _get_wb(db_id)
        sheetname, rangename = range_name.split("!")
        response = wb.worksheet(sheetname).append_rows(values=value,
                                            value_input_option='USER_ENTERED',
                                            table_range=rangename)
        return response
    except Exception as e:
        st.write(e)


def download_data_in_batch():
    pass
# def download_data(db_id,range_name,major_dimention='ROWS'):
#     """
#     * for sheet choose value from
#     1. database
#     2. sadhana card
#     """    
#     if creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#     try:
#         service = build('sheets', 'v4', credentials=creds)

#         # Call the Sheets API
#         spreadsheetID = db_list[db_id]
#         result = service.spreadsheets().values().get(
#             spreadsheetId=spreadsheetID,
#             range=range_name,
#             majorDimension=major_dimention
#             ).execute()

#         values = result.get('values', [])
#         return values
#     except HttpError as err:
#         # st.write(err)
#         pass

# def upload_data(db_id,range_name,value,input_type='RAW'):
#     """
#     * for sheet choose value from
#     1. database
#     2. sadhana card    
#     """
#     if creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#     try:
#         service = build('sheets', 'v4', credentials=creds)

#         # Call the Sheets API
#         body = {
#             'values': value
#         }
#         spreadsheetID = db_list[db_id]
#         result = service.spreadsheets().values().update(
#             spreadsheetId=spreadsheetID, range=range_name,
#             valueInputOption=input_type, body=body,
#             includeValuesInResponse=True
#             ).execute()
        
#         return result#['updatedData']
#     except HttpError as err:
#         st.write(err)
#         pass


# def append_data(db_id,range_name,value,input_type='RAW'):
#     """
#     * for sheet choose value from
#     1. database
#     2. sadhana card    
#     """
#     if creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#     try:
#         service = build('sheets', 'v4', credentials=creds)

#         # Call the Sheets API
#         body = {
#             'values': value
#         }
#         spreadsheetID = db_list[db_id]
#         result = service.spreadsheets().values().append(
#             spreadsheetId=spreadsheetID, range=range_name,
#             valueInputOption=input_type, body=body,
#             insertDataOption = 'INSERT_ROWS',
#             includeValuesInResponse=True
#             ).execute()
        
#         return result['updates']
#     except HttpError as err:
#         st.write(err)
#         pass

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
