import gspread
from oauth2client.service_account import ServiceAccountCredentials

# streamlit secret
import streamlit as st

# ========================= Some constants
# sheets
sheets_dict = st.secrets['database']

db_primary = sheets_dict['base']
db_sadhana_card = sheets_dict['sadhana_card']
db_article_tagging = sheets_dict['article_tagging']
db_accounts = sheets_dict['accounts']
db_hearing = sheets_dict['hearing_tracker']
db_plan4krsna = sheets_dict['plan4krishna']
db_psadhana_encyclopaedia = sheets_dict['p_reading_hearing_notes']
db_ssong = sheets_dict['ssong']

db_list = {1:db_primary,
           2:db_sadhana_card,
           3:db_article_tagging,
           4:db_accounts,
           5:db_hearing,
           6:db_plan4krsna,
           7:db_psadhana_encyclopaedia,
           8:db_ssong
            }

# credentials
credentials_info = st.secrets['service_account']
sc_credentialinfo = st.secrets['service_acc_sc']
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

# ========================= Some constants end
def _get_wb(db_id):
    if f'spreadsheet{db_id}' not in st.session_state:
            if db_id ==2:
                gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(sc_credentialinfo,SCOPE))
            else:    
                gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(credentials_info,SCOPE))

            workbook = gc.open_by_key(db_list[db_id])
            st.session_state[f'spreadsheet{db_id}'] = workbook
            # workbook.worksheet('jai').update(values=[[]],range_name='',raw=False)

    return st.session_state[f'spreadsheet{db_id}']

def download_data(db_id,range_name):
    """
    * for sheet choose value from
    1:db_primary,
    2:db_sadhana_card,
    3:db_article_tagging,
    4:db_accounts,
    5:db_hearing,
    6:db_plan4krsna,
    7:db_psadhana_encyclopaedia
    sheet!range in A1 notation
    """
    try:            
        workbook = _get_wb(db_id)
        if '!' in range_name:
            sheetname, rangename = range_name.split("!")
            response = workbook.worksheet(sheetname).get_values(rangename)        
            return response
        return -1

    except Exception as e:
        st.error("Something Went Wrong")
        st.write(e)

def upload_data(db_id,range_name,value):
    """
    * for sheet choose value from
    1:db_primary,
    2:db_sadhana_card,
    3:db_article_tagging,
    4:db_accounts,
    5:db_hearing,
    6:db_plan4krsna,
    7:db_psadhana_encyclopaedia
    """
    workbook = _get_wb(db_id)
    sheetname, rangename = range_name.split("!")
    response = workbook.worksheet(sheetname).update(rangename,
                                value,
                                value_input_option='USER_ENTERED')
    return response



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
        st.error("Something went Wrong")
        st.write(e)