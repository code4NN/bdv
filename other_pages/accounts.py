import streamlit as st
import datetime
import json
import pandas as pd
import calendar
from st_aggrid import AgGrid, GridOptionsBuilder

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data
from acc_expense_page import monthdbclass

class account_Class:
    def __init__(self):
        
        # sub page related information
        self.page_config = {'page_title': "BDV",
                            'page_icon':'☔',
                            'layout':'wide'}
        self.page_map = {
            'income':self.income_page,
            'expense':self.expense_page,
            'dashboard':self.dashboard_page,
        }
        self.expense_class = monthdbclass()
        self.current_page = 'dashboard'

        # databases
        self._income_database = None
        self._income_database_refresh = True
        self._income_database_range = 'income!A:E'
        # changes in db
        self._change_in_income_regular_db = 0
        self._change_in_income_others_db = 0

    
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)

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
            
            metadata = dict(zip(_income_database['key'],_income_database['value']))
            
            self._income_database = {'df':_income_database.copy(),
                                     'mdata':metadata}
            self._income_database_refresh = False

            return self._income_database
        else:
            return self._income_database
   
   
    def _switch_page(self,page):
        self.current_page = page
    
    def income_page(self):
        st.markdown(
        """
        <style>
        .step-up,
        .step-down {
            display: none;
        }
        </style>
        </style>
        """,
        unsafe_allow_html=True
        )

        incomedatabase = self.income_database
        incomedata = incomedatabase['df']
        imdta = incomedatabase['mdata']
        # st.dataframe(incomedata)

                
        # st.write(metadata)
        with st.sidebar:
            all_months = { index:monthname for index,monthname in enumerate(incomedata['month'].tolist()) if monthname!=''}
            active_index = st.radio("Choose Month",options=all_months.keys(),
                     format_func=lambda x: all_months[x],
                     index=int(imdta['active_row']))
            
        
        active_month_name = incomedata.month.tolist()[active_index]
        active_regular_df = pd.read_json(incomedata['regular'].tolist()[active_index],orient='records')

        cols = st.columns(2)
        cols[0].button("Go to Expense Page",on_click=self._switch_page,args=['expense'])
        cols[1].button("Go to Dashboard Page",on_click=self._switch_page,args=['dashboard'])

        st.markdown(f'# Rent and Prasadam for :violet[{active_month_name}]')

        def count_changes_regular():
            self._change_in_income_regular_db += 1

        showonly = st.radio(":green[Show Only ]",options=['pending','done','confirmed','all'],horizontal=True)
        st.markdown("")
        if showonly !='all':
            filtereddf = active_regular_df.query(f"Status == '{showonly}' ")
            remainingdf = active_regular_df.query(f"Status != '{showonly}' ")

            modified_active_regular_df = st.data_editor(filtereddf,
                                    hide_index=True,
                                    column_config={
                                        'Name': "Name",
                                        'Amount':st.column_config.NumberColumn("₹"),
                                        'Account':st.column_config.TextColumn("account"),
                                        'Date of Payment': st.column_config.TextColumn("Payment Date"),
                                        'Remark': st.column_config.TextColumn("remark"),
                                        'Status': st.column_config.SelectboxColumn("status",options=['pending','done','confirmed'])
                                    },
                                    on_change=count_changes_regular)
            modified_active_regular_df = pd.concat([modified_active_regular_df,remainingdf],axis=0)

        else:
            modified_active_regular_df = st.data_editor(active_regular_df,
                                    hide_index=True,
                                    column_config={
                                        'Name': "Name",
                                        'Amount':st.column_config.NumberColumn("₹"),
                                        'Account':st.column_config.TextColumn("account"),
                                        'Date of Payment': st.column_config.TextColumn("Payment Date"),
                                        'Remark': st.column_config.TextColumn("remark"),
                                        'Status': st.column_config.SelectboxColumn("status",options=['pending','done','confirmed'])
                                    },
                                    on_change=count_changes_regular)
            
        def update_monthdb(modified_dataframe):
                    upload_data(4,
                                f'income!D{active_index+2}',
                                [[f"{modified_dataframe.to_json(orient='records')}"]],
                    )
                    self._income_database_refresh=True
                    self._change_in_income_regular_db = 0                                      
        if self._change_in_income_regular_db ==0:
            st.success("All updated")
        else:
            st.button(f"Update {self._change_in_income_regular_db} Changes",on_click=update_monthdb,args=[modified_active_regular_df])
        


        st.divider()
        st.markdown("### Actions")
        action = st.radio("'",options=['Add New','Remove'],horizontal=True,label_visibility='hidden')
        if  action== 'Add New':
             name = st.text_input("Name",key='enter_new_name')
             if name:
                def add_new_name(name):
                    mydf = active_regular_df.copy()
                    newdf = pd.DataFrame.from_dict({'Name':[name],
                                 'Amount':[0],
                                 'Account':[''],
                                 'Date of Payment':[''],
                                 'Remark':[''],
                                 'Status':['pending']},orient='columns')
                    mydf = pd.concat([mydf,newdf],axis=0).reset_index(drop=True)
                    if upload_data(4,
                                 f'income!D{active_index+2}',
                                 [[f"{mydf.to_json(orient='records')}"]]
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

        st.divider()
        st.markdown(f"# Other incomes in :violet[{active_month_name}]")
        
        active_othersdf = pd.read_json(incomedata['others'].tolist()[active_index],orient='records')        
        if len(active_othersdf) ==0:
             st.write("No Entries")
        else:
            def count_change_others():
                self._change_in_income_others_db +=1
            def update_change_indf(modified_df):
                upload_data(4,
                                f'income!E{active_index+2}',
                                [[f"{modified_df.to_json(orient='records')}"]],
                    )
                self._income_database_refresh=True
                self._change_in_income_others_db = 0

            modified_df = st.data_editor(active_othersdf,hide_index=True,on_change=count_change_others)
            
            if self._change_in_income_others_db ==0:
                st.success("All updates are synced")
            else:
                st.button(f"Update {self._change_in_income_others_db} Changes",on_click=update_change_indf,
                          args=[modified_df],type='secondary')
        
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
                            dfjson = f"{df.to_json(orient='records')}"

                            if upload_data(4,f"income!E{2+active_index}",
                                        [[dfjson]]):
                                self._income_database_refresh=True
                                st.session_state['other_key_1'] = ''
                                st.session_state['other_key_2'] = 0
                                st.session_state['other_key_3'] = ''
                                st.session_state['other_key_4'] = ''
                                st.session_state['other_key_5'] = ''

                        else:
                            df = active_othersdf
                            newdf = pd.DataFrame.from_dict({"Name":[name],
                                    'Amount':[amount],
                                    'Account':[account],
                                    'Date of Payment':[dateofpayment],
                                    'Agenda or Remark':[agenda]},orient='columns')
                            df = pd.concat([active_othersdf,newdf],axis=0)
                            df.reset_index(drop=True,inplace=True)

                            dfjson = f"{df.to_json(orient='records')}"

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
        
        
        with st.sidebar:
            st.divider()
            st.header(f"Prepare Data for {imdta['next_month_name']}")
            def update_next_month():
                next_meta_data = [[imdta['next_month']],
                                [imdta['next_year']],
                                [imdta['next_row']]]
                upload_data(4,'income!B2:B4',next_meta_data)
                

                nextmonthdf = active_regular_df.copy()
                nextmonthdf['Amount'] = 0
                nextmonthdf['Account'] = ''
                nextmonthdf['Date of Payment'] = ''
                nextmonthdf['Remark'] = ''
                nextmonthdf['Status'] = 'pending'
                nextmonthdfjson = f"{nextmonthdf.to_json(orient='records')}"

                upload_data(4,f"income!C{active_index+3}:E{active_index+3}",
                            [[imdta['next_month_name'],nextmonthdfjson,f"{[]}"]])
                self._income_database_refresh=True
                st.session_state['next_month_checkbox'] = False
                
            if st.checkbox("Are you Sure",key='next_month_checkbox'):
                st.caption("This will create next month's data and activate also")

                st.button(f"Create {imdta['next_month_name']}",on_click=update_next_month)

    def expense_page(self):
        self.expense_class.display()
        st.divider()
        cols = st.columns(2)
        cols[0].button("Go to Income Page",on_click=self._switch_page,args=['income'])
        cols[1].button("Go to Dashboard Page",on_click=self._switch_page,args=['dashboard'])
        
    
    def dashboard_page(self):

        # incomedata = self.income_database
        # income_metadata = dict(zip(incomedata['key'],incomedata['value']))
        # income_active_index = int(income_metadata['active_row'])
        # income_active_month_name = incomedata.month.tolist()[income_active_index]
        # income_active_regular_df = pd.read_json(incomedata['regular'].tolist()[income_active_index],orient='records')

        
        # expensedata = self.expense_database
        # metadata = dict(zip(expensedata['key'],expensedata['value']))       

        # expense_active_index = int(metadata['active_row'])
        # expense_active_month_name = expensedata.month.tolist()[expense_active_index]
        # expense_active_monthdf = pd.read_json(expensedata['data'].tolist()[expense_active_index],orient='records')
        # department_dict = json.loads(metadata['department_dict'])


        st.header("Welcome to Accounts 💸💰")
        st.markdown("#### Active Month: ")

        cols = st.columns(2)
        
        cols[0].button("Income Page",on_click=self._switch_page,args=['income'])
        cols[1].button("Expense Page",on_click=self._switch_page,args=['expense'])
        
        def global_switch(page):
            self.bdvapp.current_page = page
        st.button("Go To Settlements",on_click=global_switch,args=['settlement'])

        # show a month-wise summary
        # Choose the month (ask the user to select and by default it is the latest month)
            # Better store in class
        
        # Create two tabs left and right
        
        # tab1 Show Income ----------------------
        # a button to open deep-dive income page
        # Show the table for rent payment
        # Show the table for other's income
        # Display total collected, total remaining

        # tab2 Show expense ----------------------
        # a button to open deep-dive expense page

        # department wise summary
            # spent
        # have a filter on these departments
        # on the processed data
        # further filters as
            # is pending
            # sub_department
        # display a table 
        # button to sync with the database
        # st.divider()
        # if st.checkbox("Edit monthly sample input"):
        #     expensedata = self.expense_database
        #     metadata = dict(zip(expensedata['key'],expensedata['value']))
        #     sampleinput = pd.read_json(metadata['next_month_prefill'],orient='records')
        #     st.data_editor(sampleinput,
        #                    num_rows='dynamic')

        
    def run(self):
        self.page_map[self.current_page]()
