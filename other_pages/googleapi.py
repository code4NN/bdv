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

def download_sheet(db_id,sheet_name):
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
    workbook = _get_wb(db_id)
    response = workbook.worksheet(sheet_name).get_all_values()
    return response

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
    workbook = _get_wb(db_id)
    if '!' in range_name:
        sheetname, rangename = range_name.split("!")
        response = workbook.worksheet(sheetname).get_values(rangename)        
        return response
    return -1

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

# class google_api_connector:
    # def __init__(self):
    #     self.account_list = [
    #         'bdv_central',
    #         'bdv_nimai',
    #         'bdv_nitai',
    #         'bdv_gopinathji',
    #         'bdv_gopalji'
    #         ]
    #     self.service_account_dict = {
    #         k:st.secrets[k] for k in self.account_list
    #     }
    #     self.active_service_account = 0
        
    #     self.workbook_dict = {
    #         'central_db':{
    #             'id':st.secrets['sheet_id_dict']['central_db'],
    #             'connections':{}
    #             # 'service_account_name':gspread instance
    #         }
    #     }
        
    # @property
    # def get_workbook(self,workbook_name):
        
    #     # get active service account to be used
    #     # change the active account after use
    #     active_account_name  = self.account_list[self.active_service_account]
    #     active_account_instance = self.service_account_dict[active_account_name]
        
    #     available_connections = self.workbook_dict[workbook_name]['connections']
        
    #     if active_account_name in available_connections.keys():
    #         # connection from the active service account already exits
    #         connection = available_connections[active_account_name]
    #     else:
    #         # create new connection
    #         connection = (gspread
    #               .authorize(ServiceAccountCredentials
    #                          .from_json_keyfile_dict(active_account_instance,
    #                                                  SCOPE)
    #                          )
    #               )
    #         connection = connection.open_by_key(self.workbook_dict[workbook_name]['id'])
            
    #         self.workbook_dict[workbook_name]['connections'][active_account_name] = connection
        
    #     # change the active service account
    #     # essentially round robin
    #     if self.active_service_account < len(self.account_list)-1:
    #         self.active_service_account += 1
    #     else :
    #         self.active_service_account = 0

    #     return connection
        
    # def download_sheet(self,workbook_name, sheet_name):
    #     workbook = self.get_workbook(workbook_name)
    #     response = workbook.worksheet(sheet_name).get_all_values()
    #     return response
    
    # def download_data(self,workbook_name,range_name):
        
    #     workbook = self.get_workbook(workbook_name)
        
    #     sheetname, rangename = range_name.split("!")
    #     response = workbook.worksheet(sheetname).get_values(rangename)        
    #     return response
    
    # def upload_data(self,workbook_name,range_name,upload_data):
    #     workbook = self.get_workbook(workbook_name)
        
    #     sheetname, rangename = range_name.split("!")
    #     response = workbook.worksheet(sheetname).update(rangename,
    #                                 upload_data,
    #                                 value_input_option='USER_ENTERED')
    #     return response
    
    # def append_data(self,workbook_name,range_name,upload_data):
        
    #     workbook = self.get_workbook(workbook_name)
    #     sheetname, rangename = range_name.split("!")
    #     response = workbook.worksheet(sheetname).append_rows(values=upload_data,
    #                                         value_input_option='USER_ENTERED',
    #                                         table_range=rangename)
    #     return response