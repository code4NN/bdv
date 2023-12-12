import streamlit as st
import datetime
import json
import pandas as pd
import calendar


from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data

class account_Class:
    def __init__(self) -> None:
        
        # sub page related information
        self.page_map = {
            'income':self.income_page
        }
        self.current_page = 'income'


        # databases
        self._income_database = None
        self._income_database_refresh = True
        self._income_database_range = 'income!A:E'
    
    @property
    def income_database(self):
        """
        1. downloads the data if refresh is True
        2. else returns the database
        Actions
            1. download and save in the class
            3. set the refresh to False
            4. return
        """
        if self._income_database_refresh:
            # download a fresh data
            # update database and refresh to False
            # return
            _income_database = download_data(4,self._income_database_range)
            _income_database = pd.DataFrame(_income_database[1:],columns=_income_database[0])
            
            self._income_database = _income_database.copy()
            self._income_database_refresh = False

            return self._income_database
        else:
            return self._income_database
    
    def income_page(self):

        incomedata = self.income_database
        st.dataframe(incomedata)

        metadata = dict(zip(incomedata['key'],incomedata['value']))        
        st.write(metadata)

        active_index = int(metadata['active_row'])
        active_month_name = incomedata.month.tolist()[active_index]
        active_regular_df = pd.read_json(json.loads(incomedata['regular'].tolist()[active_index]),orient='records')

        st.markdown(f'## Rent and Prasadam for :violet[{active_month_name}]')
        modified_active_regular_df = st.data_editor(active_regular_df,
                                  hide_index=True,
                                  column_config={
                                       'Name': "Name",
                                       'Amount':st.column_config.NumberColumn("₹"),
                                       'Account':st.column_config.TextColumn("account"),
                                       'Date of Payment': st.column_config.TextColumn("Payment Date"),
                                       'Remark': st.column_config.TextColumn("remark"),
                                       'Status': st.column_config.SelectboxColumn("status",options=['pending','done','confirmed'])
                                  })
        def update_monthdb(modified_dataframe):
                    upload_data(4,
                                f'income!D{active_index+2}',
                                [[json.dumps(modified_dataframe.to_json(orient='records'))]],
                    )
                    self._income_database_refresh=True                    

        st.button(f"Update Changes",on_click=update_monthdb,args=[modified_active_regular_df])
        


        st.divider()
        st.markdown("### Actions")
        action = st.radio("'",options=['','Add New','Remove','Next Month'],horizontal=True,label_visibility='hidden')
        if  action== 'Add New':
             name = st.text_input("Name",key='enter_new_name')
             if name:
                def add_new_name(name):
                    mydf = active_regular_df.copy()
                    mydf=mydf.append({'Name':name,
                                 'Amount':0,
                                 'Account':'',
                                 'Date of Payment':'',
                                 'Remark':'',
                                 'Status':'pending'},ignore_index=True)
                    if upload_data(4,
                                 f'income!D{active_index+2}',
                                 [[json.dumps(mydf.to_json(orient='records'))]]
                                 ):
                        st.session_state['enter_new_name'] = ''
                        self._income_database_refresh=True
                st.button(f"Add {name}",on_click=add_new_name,args=[name])

        elif action == 'Remove':
            current_list = active_regular_df.Name.tolist()
            to_drop = []
            for i,name in enumerate(current_list):
                if st.checkbox(name,key=f"drop_checkbox_{i}"):
                    to_drop.append(name)                
            
            if len(to_drop) == len(current_list):
                 st.error("you cannot drop everything")
            else:
                modified_data = modified_active_regular_df.query(f" Name not in {to_drop}")
                st.button("Remove Selected",on_click=update_monthdb,args=[modified_data])

        elif action == 'Next Month':
             
            def update_next_month():
                next_meta_data = [[metadata['next_month']],
                                [metadata['next_year']],
                                [metadata['next_row']]]
                upload_data(4,'income!B2:B4',next_meta_data)
                

                nextmonthdf = active_regular_df.copy()
                nextmonthdf['Amount'] = 0
                nextmonthdf['Account'] = ''
                nextmonthdf['Date of Payment'] = ''
                nextmonthdf['Remark'] = ''
                nextmonthdf['Status'] = 'pending'
                nextmonthdfjson = json.dumps(nextmonthdf.to_json(orient='records'))
                upload_data(4,f"income!C{active_index+3}:E{active_index+3}",
                            [[metadata['next_month_name'],nextmonthdfjson,json.dumps([])]])
                self._income_database_refresh=True

            st.button("Update",on_click=update_next_month)
        
        st.divider()
        st.divider()
        st.divider()
        st.markdown(f"## Other incomes in :violet[{active_month_name}]")
        
        active_othersdf = pd.read_json(json.loads(incomedata['others'].tolist()[active_index]),orient='records')        
        if len(active_othersdf) ==0:
             st.write("No Entries")
        else:
            st.data_editor(active_othersdf,hide_index=True)
        
        st.divider()
        with st.container():
            cols = st.columns(3)
            with cols[0]:
                name = st.text_input("Name",key='other_key_1')
                amount = st.number_input("Amount",0,step=500,key='other_key_2')
            with cols[1]:
                account = st.text_input("Account",key='other_key_3')
                dateofpayment = st.text_input("Date of payment",key='other_key_4')
            with cols[2]:
                agenda = st.text_input("Agenda or remark",key='other_key_5')

                def formsubmit(name,amount,account,dateofpayment,agenda):
                        if len(active_othersdf) ==0:
                            # base case for this month
                            data = {"Name":[name],
                                    'Amount':[amount],
                                    'Account':[account],
                                    'Date of Payment':[dateofpayment],
                                    'Agenda or Remark':[agenda]}
                            df = pd.DataFrame(data)
                            dfjson = json.dumps(df.to_json(orient='records'))
                            if upload_data(4,f"income!E{2+active_index}",
                                        [[dfjson]]):
                                self._income_database_refresh=True
                                st.session_state['other_key_1'] = ''
                                st.session_state['other_key_2'] = 0
                                st.session_state['other_key_3'] = ''
                                st.session_state['other_key_4'] = ''
                                st.session_state['other_key_5'] = ''

                        else:
                            df = active_othersdf.append({"Name":name,
                                    'Amount':amount,
                                    'Account':account,
                                    'Date of Payment':dateofpayment,
                                    'Agenda or Remark':agenda},ignore_index=True)
                            df.reset_index(drop=True,inplace=True)
                            dfjson = json.dumps(df.to_json(orient='records'))
                            if upload_data(4,f"income!E{2+active_index}",
                                        [[dfjson]]):
                                self._income_database_refresh=True
                                st.session_state['other_key_1'] = ''
                                st.session_state['other_key_2'] = 0
                                st.session_state['other_key_3'] = ''
                                st.session_state['other_key_4'] = ''
                                st.session_state['other_key_5'] = ''

                if name and amount and account and dateofpayment and agenda:
                    st.button("Submit",on_click=formsubmit,args=[name,amount,account,dateofpayment,agenda])
                else:
                    st.button("Submit",disabled=True,help="Please fill all the fields")





    
    def run(self):
        self.page_map[self.current_page]()
