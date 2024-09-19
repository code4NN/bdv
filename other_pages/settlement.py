import streamlit as st
import pandas as pd

import pytz
import datetime


from other_pages.googleapi import download_data



class settlement_class_new:
    def __init__(self):
        
        self.page_config = {'page_title': "settlements",
                            'page_icon':'💸',
                            'layout':'centered'}
        self.page_dict = {
            'active':'settlement_form',
            'settlement_form':self.request_settlement,
            'do_settlement':self.process_settlement,
        }
        
        # database
        self._bookdb = None
        self._refresh_book = True
        self._format_datetime = {'timestamp':"%Y%b%d %H%M%S",
                                 'paymnt_date':"on %Y%B%d"}
    
    @property
    def bookdb(self):
        if self._refresh_book:
            dbarray = download_data(1,'bdv_settlement!A1:G')
            dbdf = pd.DataFrame(dbarray[1:], columns=dbarray[0])
            
            # convert the column types
            dbdf['amount'] = pd.to_numeric(dbdf['amount'])
            dbdf['timestamp'] = pd.to_datetime(dbdf['timestamp'],format=self._format_datetime['timestamp'])
            dbdf['paymnt_date'] = pd.to_datetime(dbdf['paymnt_date'],format=self._format_datetime['paymnt_date'])
            
            
            def summarize_dev_data(user_phone_id_id):
                # get the data for the user and sort it
                relevant_data = dbdf.query(f" user_phone_id == '{user_phone_id_id}' ").copy(deep=True)
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
        def _take_one_entry_():
            request = {}
            request['timestamp'] = datetime.datetime.now(india_timezone).strftime(self._format_datetime['timestamp'])
            request['is_settlement'] = 'no'
            request['user_phone_id'] = f"sid_{userinfo['phone_number']}"
            request['full_name'] = userinfo['full_name']
            left,right = st.columns(2)
            with left:
                request['paymnt_date'] = st.date_input("Payment Date",
                                                    value=datetime.date.today(),
                                                    format="YYYY-MMM-DD",
                                                    #    min_value=
                                                    )
            with right:
                request['amount'] = st.number_input("Amount",step=1)
            left,right = st.columns(2)
            with left:
                st.radio("Department")
            with right:
                st.text_input("Agenda")
            
            return request
        
        # show active settlements
        # show historical settlements
        
    
    
    
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