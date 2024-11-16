import streamlit as st
import pandas as pd
import json

import pytz
import datetime


from other_pages.googleapi import download_data,append_data,upload_data


class settlement_class_new:
    def __init__(self):
        
        self.page_config = {'page_title': "settlements",
                            'page_icon':'💸',
                            'layout':'centered'}
        self.page_map = {
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
            # current columns [timestamp
            #                  is_settlement
            #                  user_phone_id
            #                  full_name
            #                  details
            #                  status
            #                   ]
            # details will be expanded to [paymnt_date, amount, department, agenda]
            # st.dataframe(dbdf)
            dbdf['details'] = dbdf['details'].apply(lambda x: json.loads(x))
            # now flatten the data
            flatten_data_list = []
            final_columns = ['timestamp',
                            'is_settlement',
                            'user_phone_id',
                            'full_name',
                            'paymnt_date',
                            'amount',
                            'department',
                            'agenda',
                            'status',
                            'dbrow']
            for _, row in dbdf.iterrows():
                an_entry_fixed_values = [row['timestamp'],
                            row['is_settlement'],
                            row['user_phone_id'],
                            row['full_name']]
                one_entry = []
                for one_payment_dict in row['details']:
                    one_payment_values = [one_payment_dict['paymnt_date'],
                                          one_payment_dict['amount'],
                                          one_payment_dict['department'],
                                          one_payment_dict['agenda']
                                          ]
                    one_entry.append([*an_entry_fixed_values,
                                      *one_payment_values,
                                      row['status'],
                                      row['dbrow']
                                      ])
                flatten_data_list.extend(one_entry)
            
            dbdf = pd.DataFrame(flatten_data_list,
                                columns=final_columns,
                                )

            dbdf['paymnt_date'] = pd.to_datetime(
                                    dbdf['paymnt_date'],
                                    format=self._format_datetime['paymnt_date']
                                                  )
            dbdf['amount'] = pd.to_numeric(dbdf['amount'],
                                           downcast='integer')            
            
            # convert the column timestamp to time
            dbdf['timestamp'] = pd.to_datetime(dbdf['timestamp'],
                                                format=self._format_datetime['timestamp'])
            
            # st.dataframe(dbdf)
            def summarize_dev_data(user_phone_id):
                # get the data for the user and sort it
                relevant_data = dbdf.query(f" user_phone_id == '{user_phone_id}' ").copy(deep=True)
                user_name = relevant_data['full_name'].unique().tolist()[0]
                relevant_data.sort_values(by=['paymnt_date','timestamp'],
                                          ascending=[True,True],
                                          inplace=True)
                relevant_data.reset_index(drop=True, inplace=True)
                
                # create account balance based on history
                relevant_data['acc_balance'] = relevant_data['amount'].cumsum()
                
                # debug
                # st.dataframe(relevant_data)
                
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
                    
                    # get last settlement
                    last_settlement_date = relevant_data.query("is_settlement == 'yes' ")['paymnt_date'].max()
                else:
                    historical_data = [relevant_data]
                    active_data = relevant_data
                    last_settlement_date = relevant_data['paymnt_date'].min()
                
                return {'historical_statement':historical_data,
                        'last_settlement_date':last_settlement_date,
                        'active_statement':active_data,
                        'nodata':False,
                        'name':user_name
                        
                        }
            
            unique_ids = dbdf['user_phone_id'].unique().tolist()
            if unique_ids:
                dev_dict = {pid:summarize_dev_data(pid) for pid in unique_ids}
            
            user_phone_id = f"sid_{self.bdv.userinfo['phone_number']}"
            
            # when there is no entry
            if user_phone_id not in dev_dict.keys():
                dev_dict[user_phone_id] = {
                    'nodata':True
                }
            self._bookdb = {
                'dict':dev_dict,
                'my_sid':user_phone_id,
                'user_book':dev_dict[user_phone_id]
            }
            self._refresh_book = False
            
        return self._bookdb
    
    @property
    def bdv(self):
        return st.session_state['bdv_app']
        
    def request_settlement(self):
        
        userinfo = self.bdv.userinfo
        st.markdown(f"### :rainbow[Hare Krishna] :gray[{userinfo['full_name']}] ")
        
        if 'admin' in userinfo['global_roles']:
            st.button("Settlements",
                    on_click=lambda x: self.page_map.__setitem__("active","settle"),
                    args=['dummy']
                    )
        
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
                is_nts = self.bookdb['user_book']['nodata']
                if is_nts:
                    request['paymnt_date'] = st.date_input("Payment Date",
                                                        value=datetime.date.today(),
                                                        # format="YYYY/MMM/DD",
                                                        key=f"date_input_{prefix}",
                                                        max_value=datetime.datetime
                                                        .now(india_timezone)
                                                        )
                else:
                    last_settlement_date = self.bookdb['user_book']['last_settlement_date']
                    request['paymnt_date'] = st.date_input("Payment Date",
                                                        value=datetime.date.today(),
                                                        # format="YYYY/MMM/DD",
                                                        key=f"date_input_{prefix}",
                                                        min_value= last_settlement_date,
                                                        max_value=datetime.datetime
                                                        .now(india_timezone)
                                                        )
                st.caption(request['paymnt_date'].strftime("%d %b %A"))
                request['paymnt_date'] = request['paymnt_date'].strftime(self._format_datetime['paymnt_date'])
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
                                                     "Preaching",
                                                     "Guest",
                                                     "EM",
                                                     "Deity",
                                                     "other"
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
        self._count_request = st.number_input("Count requests",
                                              min_value=1,
                                              max_value=10)
        
        for i in range(self._count_request):
            prefix = f"request_{i}"
            st.divider()
            st.markdown(f"#### :gray[Entry no: ] {i+1}")
            valid_input, request = _take_one_entry_(prefix)
            all_request['details'].append(request)
            all_valid_input = all_valid_input * valid_input
            
        if all_valid_input==1:
            st.success("All fields have been filled properly")
            df2show = pd.DataFrame.from_dict(all_request['details'])
            df2show['paymnt_date'] = (pd.to_datetime(df2show['paymnt_date'],
                                                    format=self._format_datetime['paymnt_date']
                                                    )
                                      .apply(lambda x:x.strftime("%d %b %a")
                                             )
                                      )
            st.dataframe(df2show,hide_index=True)
            # st.write(json.dumps(all_request['details']))
            def push_data(request_dict):
                column_order = ['timestamp',
                                'is_settlement',
                                'user_phone_id',
                                'full_name',
                                'details',
                                'status']
                request_dict['details'] = json.dumps(request_dict['details'])
                payload = [[request_dict[i] for i in column_order]]
                # st.write(payload)
                append_data(1,
                            "bdv_settlement!A:F",
                            value=payload
                            )
                self._count_request = 1
                self._refresh_book = True
                
            st.button("Submit",
                      on_click=push_data,
                      args=[all_request])
            
        else:
            st.error("Please fill all the fields")
        
        
        
        st.divider()
        user_book = self.bookdb['user_book']
        
        if user_book['nodata']:
            st.markdown("### :orange[No any requests yet]")
            return
        
        last_settled_date = user_book['last_settlement_date'].strftime("%d %b %A")
        active_settlements = user_book['active_statement']
        
        st.markdown(f"### :gray[Last day when your account was settled was] :blue[{last_settled_date}]")
        st.markdown(f"### :gray[Current unsettled expenses sums to] :orange[{active_settlements['amount'].sum()} ₹]")
        # show active settlements
        st.caption("Showing Details")
        columns_to_show = [
            'paymnt_date','acc_balance','amount','agenda','department',
        ]
        showdb = user_book['active_statement'][columns_to_show]
        showdb['paymnt_date'] = showdb['paymnt_date'].apply(lambda x: x.strftime("%d %b %a"))
        showdb.columns = ['spent on','total pending','amount','agenda','dept']
        st.dataframe((showdb.style.
                      highlight_between(subset=['amount'],left=-1000,
                                        right=-0.1,
                                        color='yellow')),
                     hide_index=True)
        # show historical settlements
        st.divider()
        if st.checkbox("Show historical bank statement"):
            for key_,a_chunk in enumerate(reversed(user_book['historical_statement'])):
                st.divider()
                date_min,date_max = a_chunk['paymnt_date'].min().strftime("%d %b %a"),a_chunk['paymnt_date'].max().strftime("%d %b %a")
                
                columns_to_show = [
                    'paymnt_date','acc_balance','amount','agenda','department',
                ]
                showdb = a_chunk[columns_to_show]
                
                showdb['paymnt_date'] = showdb['paymnt_date'].apply(lambda x: x.strftime("%d %b %a"))
                showdb.columns = ['spent on','total pending','amount','agenda','dept']
                
                st.markdown(f"### :gray[expenses between] :blue[{date_min}] :gray[and] :orange[{date_max}]")
                st.dataframe((showdb.style.
                            highlight_between(subset=['amount'],left=-1000,
                                                right=-0.1,
                                                color='yellow')),
                            hide_index=True,
                            key=f"{key_}_historic_data"
                            )
                st.divider()
        
    def bank_statement(self):
        pass
    
    
    def process_settlement(self):
        
        st.button("back to request page",
                  on_click=lambda x: self.page_map.__setitem__('active','request'),
                  args=[-1]
                  )
        bookdb = self.bookdb['dict']
        st.write(bookdb)
        
        active_settlement_lakshmi = {}
        for one_dev_data in bookdb.values():
            name = one_dev_data['name']
            active_settlement = one_dev_data['active_statement']
            pending_lakshmi = active_settlement['amount'].sum()
            
            active_settlement_lakshmi[name] = {'pending':pending_lakshmi,
                                               'activedf':active_settlement}
        display_pending_dict = {k:v['pending'] for k,v in active_settlement_lakshmi.items()}
        display_pending_df = (pd.DataFrame
                              .from_dict(display_pending_dict,orient='index')
                              .reset_index())
        display_pending_df.columns = ['name','unsettled']
        display_pending_df.insert(0,'pick',False)
        chosen_name = st.data_editor(display_pending_df,
                       disabled=['name','unsettled']).query("pick==True").name.tolist()
        if not chosen_name:
            st.warning("Pick one name")
        else:
            chosen_name = chosen_name[0]
            activ_df = active_settlement_lakshmi[chosen_name]['activedf']
            
            activ_df['dbrow'] = activ_df['dbrow'].apply(lambda x: int(x))
            activ_df.sort_values(by='dbrow',ascending=True,inplace=True)
            show_only_noted = st.checkbox("Show only noted ones")
            if show_only_noted:
                activ_df = activ_df.query("status=='noted'")
            for dbrow in activ_df.dbrow.unique().tolist():
                st.divider()
                one_chunk = activ_df.query(f"dbrow=={dbrow}").copy()
                timestamp = one_chunk.timestamp.tolist()[0].strftime("%d %b %a")
                status = one_chunk.status.tolist()[0]
                color = 'green' if status=='noted' else 'red'
                st.markdown(f"### :{color}[filled on]:gray[{timestamp}]")
                
                display_columns = ['paymnt_date','amount','acc_balance',
                                    'department','agenda','status']
                one_chunk['paymnt_date'] = one_chunk.paymnt_date.apply(lambda x: x.strftime("%d %b"))
                st.dataframe(one_chunk[display_columns])
                def mark_noted(dbrow):
                    upload_data(1,
                                f'bdv_settlement!F{dbrow}',
                                [['noted']])
                    self._refresh_book=True

                st.button("Mark as noted",
                             on_click=mark_noted,args=[dbrow],
                             key=f"{dbrow}_notedbtn")
            
            st.divider()
            if show_only_noted:
                # get certain details
                _user_phone_id = activ_df['user_phone_id'].unique().tolist()[0]
                _full_name =  activ_df['full_name'].unique().tolist()[0]
                _amount = activ_df.amount.sum()
                
                req_cols = ['full_name','dbrow',
                            'paymnt_date','amount',
                            'department','agenda',]
                pushdata = activ_df[req_cols].copy()
                pushdata['dbrow'] = pushdata['dbrow'].astype('str')
                pushdata.insert(0,'date',pushdata.paymnt_date.apply(lambda x: x.strftime("%Y/%m/%d")))
                pushdata.insert(0,"sid",pushdata.full_name.str.replace(" ","_").str.lower()+"_sid_"+pushdata.dbrow)
                pushdata = pushdata.drop(columns = ['full_name',
                                                   'dbrow',
                                                   'paymnt_date'])
                
                if show_only_noted:
                    paymnt_remark = st.text_input("payment remark",key='paymnt_remark')
                    paymnt_date = st.date_input("date of payment")
                    st.caption(paymnt_date.strftime("%d %m %a"))
                    paymnt_date = paymnt_date.strftime(self._format_datetime['paymnt_date'])
                    payment_amount = st.number_input("Amount",
                                                     value=_amount)
                    
                    def push_entries(payment_details,accdb,user_phone,_full_name):
                        india_timezone = pytz.timezone('Asia/Kolkata')
                        
                        payload = [(datetime.datetime
                                    .now(india_timezone)
                                    .strftime(self._format_datetime['timestamp'])),
                                   'yes',
                                   user_phone,_full_name,
                                   json.dumps(payment_details),
                                   'noneed'
                                   ]
                        append_data(1,'bdv_settlement!A:F',
                                    payload)
                        
                        append_data(1,'settlementdocs!A:E',
                                    accdb)
                    
                    _details = [{'paymnt_date':paymnt_date,
                                'amount':-1*payment_amount,
                                'department':'settlement',
                                'agenda':paymnt_remark}]
                    st.button("Settle this",
                              on_click=push_entries,
                              args=[_details,
                                    pushdata.to_numpy().tolist(),
                                    _user_phone_id,
                                    _full_name
                                    ])
            
        
    
    def run(self):
        st.markdown(
        """
        <style>
        [data-testid="stNumberInputStepDown"] {
                visibility: hidden;
            }
        [data-testid="stNumberInputStepUp"] {
                visibility: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True
        )
        if self.bdv.user_exists:
            self.page_map[self.page_map['active']]()
        else:
            # ask to login
            self.bdv.quick_login()