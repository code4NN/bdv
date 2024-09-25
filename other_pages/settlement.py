import streamlit as st
import pandas as pd
import json

import pytz
import datetime


from other_pages.googleapi import download_data



class settlement_class_new:
    def __init__(self):
        
        self.page_config = {'page_title': "settlements",
                            'page_icon':'💸',
                            'layout':'centered'}
        self.page_dict = {
            'active':'request',
            'request':self.request_settlement,
            'statement': self.bank_statement,
            'settle':self.process_settlement,
        }
        
        # page related data
        self._count_request = 1
        
        # database
        self._bookdb = None
        self._refresh_book = True
        self._format_datetime = {'timestamp':"at %Y%b%d %H%M%S",
                                 'paymnt_date':"on %Y%B%d"}
    
    @property
    def bookdb(self):
        if self._refresh_book:
            dbarray = download_data(1,'bdv_settlement!A1:G')
            dbdf = pd.DataFrame(dbarray[1:], columns=dbarray[0])
            
            # flatten the data
            # current columns ['timestamp',
            #                   'user_phone_id',
            #                   'full_name',
            #                    'details', 'status'
            #                   ]
            # details will be expanded to [paymnt_date, amount, department, agenda]
            dbdf['details'] = dbdf['details'].apply(lambda x: json.loads(x))
            dbdf['paymnt_date'] = pd.to_datetime(
                                    dbdf['details'].map(lambda x: x['paymnt_date']),
                                    format=self._format_datetime['paymnt_date']
                                                  )
            dbdf['amount'] = pd.to_numeric(dbdf['details'].map(lambda x: x['amount']),
                                           downcast='integer')
            dbdf['department'] = dbdf['details'].map(lambda x: x['department'])
            dbdf['agenda'] = dbdf['details'].map(lambda x: x['agenda'])
            dbdf.drop(columns='details', inplace=True)
            
            dbdf = dbdf[[
                'timestamp',
                'user_phone_id',
                'full_name',
                'paymnt_date',
                'amount',
                'department',
                'agenda',
                'is_settlement',
                'status'
            ]].copy()
            
            
            # convert the column timestamp to time
            dbdf['timestamp'] = pd.to_datetime(dbdf['timestamp'],format=self._format_datetime['timestamp'])
            
            
            def summarize_dev_data(user_phone_id):
                # get the data for the user and sort it
                relevant_data = dbdf.query(f" user_phone_id == '{user_phone_id}' ").copy(deep=True)
                relevant_data.sort_values(by='paymnt_date',ascending=True,inplace=True)
                relevant_data.reset_index(drop=True, inplace=True)
                
                # create account balance based on history
                relevant_data['acc_balance'] = relevant_data['amount'].cumsum()
                
                # divide the history into chunks when things were totally settled
                zero_balance_index = relevant_data.query(" acc_balance == 0 ").index.tolist()
                if zero_balance_index:
                    zero_balance_index = [i + 1 for i in zero_balance_index]
                    zero_balance_index.insert(0,0)
                    zero_balance_index.append(len(relevant_data))
                    sliced_index = [(zero_balance_index[i], zero_balance_index[i + 1]) for i in range(len(zero_balance_index) - 1)]
                    
                    historical_data = []
                    for chunk in sliced_index:
                        start_index, end_index = chunk
                        chunk_data = relevant_data.iloc[start_index:end_index].copy()
                        historical_data.append(chunk_data)                    
                    active_data = historical_data[-1]
                else:
                    historical_data = []
                    active_data = []
                # get last settlement
                last_settlement_date = relevant_data.query("is_settlement == 'yes' ")['paymnt_date'].max()
                
                return {'historical_statement':historical_data,
                        'last_settlement_date':last_settlement_date,
                        'active_statement':active_data
                        }
            
            unique_ids = dbdf['user_phone_id'].unique().tolist()
            if unique_ids:
                dev_dict = {pid:summarize_dev_data(pid) for pid in unique_ids}
            
            self._bookdb = {
                'dict':dev_dict
            }
            self._refresh_book = False
            
        return self._bookdb
    
    @property
    def bdv(self):
        return st.session_state['bdv_app']
        
    def request_settlement(self):
        
        userinfo = self.bdv.userinfo
        st.markdown(f"### :rainbow[Hare Krishna] :gray[{userinfo.full_name}] ")
        
        # show the last amount that user have filled
        
        # form filling
        india_timezone = pytz.timezone('Asia/Kolkata')
        all_request = {}
        all_request['timestamp'] = (datetime.datetime
                                .now(india_timezone)
                                .strftime(self._format_datetime['timestamp'])
                                )
        all_request['is_settlement'] = 'no'
        all_request['user_phone_id'] = f"sid_{userinfo['phone_number']}"
        all_request['full_name'] = userinfo['full_name']
        all_request['details'] = []
        all_request['status'] = 'requested' # noted
        
        def _take_one_entry_(prefix):
            """
            * paymnt_date, amount, department, agenda
            """
            valid_input = 1
            request = {}
            left,right = st.columns(2)
            with left:
                request['paymnt_date'] = st.date_input("Payment Date",
                                                    value=datetime.date.today(),
                                                    format="YYYY-MMM-DD",
                                                    key=f"date_input_{prefix}"
                                                    #    min_value=
                                                    )
            with right:
                request['amount'] = st.number_input("Amount",step=1,
                                                    key=f"amount_input_{prefix}")
                if not request['amount']:
                    st.caption(":red[Please enter amount]")
                    valid_input = 0
                
            left,right = st.columns(2)
            with left:
                request['department'] = st.radio(label="chose department",key=f"department_input_{prefix}",
                                                 options=[
                                                     
                                                 ])
                if request['department'] =='other':
                    another_department = st.text_input("which one",key=f"department_other_input_{prefix}").strip()
                    if another_department:
                        request['department'] = another_department
            with right:
                request['agenda'] = st.text_input("Agenda",key=f"agenda_input_{prefix}")
                if not request['agenda']:
                    st.caption(":red[Please enter agenda]")
                    valid_input = 0
                    
            return valid_input, request
        
        all_valid_input = 1
        for i in range(self._count_request):
            prefix = f"request_{i}"
            valid_input, request = _take_one_entry_(prefix)
            all_request['details'].append(request)
            all_valid_input = all_valid_input * valid_input
        if all_valid_input==1:
            st.success("All fields have been filled properly")
        else:
            st.error("Please fill all the fields")
        
        
            
                
        
        # show active settlements
        # show historical settlements
        
    def bank_statement(self):
        pass
    
    
    def process_settlement(self):
        pass
    
    def run(self):
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
        if self.bdv.user_exists:
            self.page_map[self.page_map['active']]()
        else:
            # ask to login
            self.bdv.quick_login()