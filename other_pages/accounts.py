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
            'income':self.income_page,
            'expense':self.expense_page,
        }
        self.current_page = 'expense'


        # databases
        self._income_database = None
        self._income_database_refresh = True
        self._income_database_range = 'income!A:E'
        # changes in db
        self._change_in_income_regular_db = 0
        self._change_in_income_others_db = 0
    
        self._expense_database = None
        self._expense_database_refresh = True
        self._expense_database_range = 'expense!A:D'
        # Changes in db
        self._chance_in_expense_db = 0

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
   
    @property
    def expense_database(self):
        """
        1. downloads the data if refresh is True
        2. else returns the database
        Actions
            1. download and save in the class
            3. set the refresh to False
            4. return
        """
        if self._expense_database_refresh:
            # download a fresh data
            # update database and refresh to False
            # return
            _expense_database = download_data(4,self._expense_database_range)
            _expense_database = pd.DataFrame(_expense_database[1:],columns=_expense_database[0])
            
            self._expense_database = _expense_database.copy()
            self._expense_database_refresh = False

            return self._expense_database
        else:
            return self._expense_database
    
    def income_page(self):

        incomedata = self.income_database
        st.dataframe(incomedata)

        metadata = dict(zip(incomedata['key'],incomedata['value']))        
        st.write(metadata)

        active_index = int(metadata['active_row'])
        active_month_name = incomedata.month.tolist()[active_index]
        active_regular_df = pd.read_json(incomedata['regular'].tolist()[active_index],orient='records')

        st.markdown(f'## Rent and Prasadam for :violet[{active_month_name}]')
        def count_changes_regular():
            self._change_in_income_regular_db += 1
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
                nextmonthdfjson = f"{nextmonthdf.to_json(orient='records')}"

                upload_data(4,f"income!C{active_index+3}:E{active_index+3}",
                            [[metadata['next_month_name'],nextmonthdfjson,f"{[]}"]])
                self._income_database_refresh=True

            st.button("Update",on_click=update_next_month)
        
        st.divider()
        st.divider()
        st.divider()
        st.markdown(f"## Other incomes in :violet[{active_month_name}]")
        
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
                            df = active_othersdf.append({"Name":name,
                                    'Amount':amount,
                                    'Account':account,
                                    'Date of Payment':dateofpayment,
                                    'Agenda or Remark':agenda},ignore_index=True)
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

    def expense_page(self):
        expensedata = self.expense_database
        st.dataframe(expensedata)
        
        metadata = dict(zip(expensedata['key'],expensedata['value']))        
        st.write(metadata)

        active_index = int(metadata['active_row'])
        active_month_name = expensedata.month.tolist()[active_index]
        active_monthdf = pd.read_json(expensedata['data'].tolist()[active_index],orient='records')
        department_dict = json.loads(metadata['department_dict'])
        st.write(department_dict)

        st.markdown(f"## Expenses for :violet[{active_month_name}]")
        
        if len(active_monthdf) == 0:
            st.write("NO DATA")
        else:
            def push_changes(modified_data):
                data2upload = f"{modified_data.to_json(orient='records')}"
                if upload_data(4,
                            f'expense!D{active_index+2}',
                            [[data2upload]]):
                    self._expense_database_refresh = True
                    self._chance_in_expense_db = 0
            def _count_changes():
                self._chance_in_expense_db +=1

            modified_month_df = st.data_editor(active_monthdf,
                                               hide_index=True,
                                               on_change=_count_changes)

            if self._chance_in_expense_db==0:
                st.success("You are up to date")
            else:
                st.button(f"Sync {self._chance_in_expense_db} Changes",
                          on_click=push_changes,args=[modified_month_df])







        st.divider()
        st.markdown("## :orange[New Entry]")
        input_department=st.radio('Department',
                 options=department_dict.keys(),
                 horizontal=True
        )
        left,right = st.columns(2)
        with left:
            input_sub_department = st.radio("Sub Department",
                                            options=[*department_dict[input_department],"OTHER"]
                                            )
            input_agenda = st.text_input("Agenda ",key='inp_agenda')
            input_agenda = input_agenda.strip()

        with right:
            input_payment_date = st.date_input("Paid on")
            input_remark = st.text_area("Remarks",height=30,key='inp_remark')
            if not input_remark:
                input_remark = "No remarks"
            if not input_agenda:
                st.button("Submit",disabled=True,help = 'Agenda cannot be blank')
            else:
                def add_an_expense(dpt,sb_dpt,agenda,pmt_date,
                                   remark,is_first=False):
                    if is_first:
                        data = {'department':[dpt],
                                'sub department':[sb_dpt],
                                'agenda':[agenda],
                                'payment date':[pmt_date],
                                'remark':[remark],
                                'status':['done']
                                }
                        data = pd.DataFrame(data)
                        data2upload = f"{data.to_json(orient='records')}"
                        if upload_data(4,
                                    f'expense!D{active_index+2}',
                                    [[data2upload]]):
                            self._expense_database_refresh = True
                            st.session_state['inp_agenda'] = ''
                            st.session_state['inp_remark'] = ''
                            self._chance_in_expense_db = 0
                    else:
                        data = active_monthdf.copy()
                        data=data.append({'department':dpt,
                                'sub department':sb_dpt,
                                'agenda':agenda,
                                'payment date':pmt_date,
                                'remark':remark,
                                'status':'done'
                                },ignore_index=True)
                        data=data.reset_index(drop=True)
                        data2upload = f"{data.to_json(orient='records')}"
                        
                        if upload_data(4,
                                    f'expense!D{active_index+2}',
                                    [[data2upload]]):
                            self._expense_database_refresh = True
                            st.session_state['inp_agenda'] = ''
                            st.session_state['inp_remark'] = ''                                                                                                
                            self._chance_in_expense_db = 0
                        
                st.button("Submit",on_click=add_an_expense,
                          args=[input_department,input_sub_department,
                          input_agenda,input_payment_date,input_remark,
                          len(active_monthdf) == 0])

        
        
    def run(self):
        self.page_map[self.current_page]()
