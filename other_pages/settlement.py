import streamlit as st
import datetime
import json
import pandas as pd
import calendar
from st_aggrid import AgGrid, GridOptionsBuilder,ColumnsAutoSizeMode

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data

class page4_settlement:
    def __init__(self):
        
        # sub page related information
        self.subpage_navigator = {
            'home':self.home,
            'makePayments':self.make_payments
        }
        self.subpage = 'home'

        # for request form
        self.REQUEST_FORM_ORDER = [
                                'timestamp',
                                'date_of_paymnt',
                                'name',
                                'request_id',
                                'amount',
                                'department',
                                'table_entry',
                                'remark'
                                ]
        self.REQUEST_FORM_RANGE = 'settlement_request!A:H'
        self.SETTLEMENT_INFO = 'settlement_request!A2:M'
        self.REQUEST_SHEET = 'settlement_request!'
        self.NOTED_IN_ACC_COL = 'I'

        self.no_of_requests = 1 # default value
        self.request_upload_response = 'none'
        

        # for payments
        self.PAYMENT_ORDER = ['timestamp',
                              'date_of_paymnt',
                              'amount',
                              'paymnt_info',
                              'remark',
                              'request_ids']
        self.PAYMENT_RANGE = 'settlement_payment!C:H'
        

        # data bases
        self._request_db = None
        self._request_db_refresh = True
    
    @property
    def request_db(self):
        """
        1. downloads the data if refresh is True
        2. else returns the database
        Actions
            1. download
            2. save
            3. set the refresh to False
            4. return
        """
        if self._request_db_refresh:

            # put logic here to download the data
            array = download_data(db_id=1,range_name=self.SETTLEMENT_INFO)            
            temp = pd.DataFrame(array[1:],columns=array[0])
            temp = temp[temp['devotee name']==st.session_state['user']['name']]
            temp = temp[['dept','timestamp','devotee name','uniqueid','amount','details','any comments','noted_in_expense_sheet','2','settlement_id','status']]
            temp.query("dept=='-'",inplace=True)
            temp['amount'] = temp['amount'].apply(lambda x: float(x))
            
            self._request_db = temp.copy()
            self._request_db_refresh = False
            return self._request_db

        else:
            return self._request_db

    def go2_subpage(self,subpage):
        """"""
        self.subpage = subpage

    def home(self):

        if st.session_state.LAYOUT != 'wide':
            st.session_state.LAYOUT = 'wide'
            st.experimental_rerun()
        
        st.markdown(
        """
        <style>
        .step-up,
        .step-down {
            display: none;
        }
        </style>
        """,
        # </style>
        unsafe_allow_html=True
        )

        st.header(" :green[settlement form]")
        # for account in charge
        if 'acc_ic' in st.session_state.user['roles']:
            st.button("Make Settlements",on_click=self.go2_subpage,args=['makePayments'],key='button_subpage4acic')
        st.markdown('---')



        # the form input and submit
        requestform = {'error':False}
        with st.expander("fill a form",expanded=True):
            
            # get the month of payment
            current_month = datetime.datetime.now().month
            current_year = datetime.datetime.now().year
            previous_month = current_month - 1 if current_month !=1 else 12
            st.header(f":violet[request-id-{st.session_state['user']['settlement_id']}]")
            request_month = st.radio("Enter month",
                                    options=[previous_month,current_month],
                                    format_func=lambda x: calendar.month_name[x],
                                    horizontal=True)
            max_day_in_rqsted_month = calendar.monthrange(current_year,request_month)[1]
            
            entry_table = []
            for i in range(self.no_of_requests):
                one_entry = {}
                col_day,col_amount,col_dept,col_details = st.columns([1,1,3,4])
                
                # date of payment
                one_entry['day'] = col_day.number_input("day",step=1,
                                    min_value=1,max_value=max_day_in_rqsted_month,
                                    key=f'input_table_day{i}')
                spent_date = datetime.datetime(current_year,request_month,one_entry['day'])

                # logic to deny older payments
                if (datetime.datetime.now() -spent_date).days > 7:
                    requestform['error'] = True
                    col_day.markdown(":red[Older than 7 days not accepted]")
                
                col_day.caption(datetime.datetime(current_year,request_month,one_entry['day']).strftime("%b %d %a"))
                one_entry['day'] = datetime.datetime(current_year,request_month,one_entry['day']).strftime("%b-%d, %a")
                
                # amount
                one_entry['amount'] = col_amount.number_input("amount",
                                        step=100,min_value=1,max_value=15000,
                                    key=f'input_table_amount{i}')
                # department
                one_entry['dept'] =  col_dept.text_input("dept",
                                    key=f'input_table_dept{i}')
                # details of payment
                one_entry['details'] = col_details.text_area("details",
                                    key=f'input_table_details{i}',height=10)
                
                # Check required fields are filled
                if not one_entry['dept'].strip():
                    col_dept.markdown(":red[cannot be blank]")
                    requestform['error'] = True

                if not one_entry['details'].strip():
                    col_details.markdown(":red[cannot be blank]")
                    requestform['error'] = True

                entry_table.append(one_entry)
                st.markdown('---')
            
            # -------to add or remove more entries
            def modify_no_of_fields(to_increment):
                if to_increment:
                    self.no_of_requests +=1
                elif self.no_of_requests ==1:
                    pass
                else:
                    st.session_state.no_of_requests -=1
            
            # add and drop button
            left,right = st.columns(2)
            left.button("Add one more entry",on_click=modify_no_of_fields,
                        key='increase_input_fields',args=[True])
            if self.no_of_requests >1:
                right.button("Drop last entry",on_click=modify_no_of_fields,
                            key='decrease_input_fields',args=[False])
            
            # collect other fields
            requestform['table_entry'] = entry_table
            # st.write(json.dumps(entry_table))
            requestform['remark'] = st.text_area("Any other remark",
                                                height=60,key='additional_remark')

            # timestamp
            requestform['timestamp'] = str(datetime.datetime.now())
            # name
            requestform['name'] = st.session_state['user']['name']
            # request ID
            requestform['request_id'] = f"{requestform['name']}-{st.session_state['user']['settlement_id']}"

            
            
            # submit function
            def request_form_submit(request_dict):
                final_entry_table = [['day','amount','dept','details']]
                total_amount = 0

                for one_entry in request_dict['table_entry']:
                    final_entry_table.append([one_entry['day'],
                                            one_entry['amount'],
                                            one_entry['dept'],
                                            one_entry['details']])
                    total_amount += int(one_entry['amount'])
                request_dict['table_entry'] = json.dumps(final_entry_table)
                # other changes
                request_dict['date_of_paymnt'] = '-'
                request_dict['department'] = '-'
                request_dict['amount'] =  total_amount

                # submit
                request_to_sheet = []
                for value in self.REQUEST_FORM_ORDER:
                    request_to_sheet.append(request_dict[value])
                request_to_sheet.append("no")
                try:
                    response  = append_data(db_id=1,range_name=self.REQUEST_FORM_RANGE,
                                value=[request_to_sheet])
                    
                    if response:
                        self._request_db_refresh = True
                        self.no_of_requests = 1
                        st.session_state.input_table_details0 = ""
                        st.session_state.input_table_dept0 = ""
                        st.session_state['user']['settlement_id'] = str(int(st.session_state['user']['settlement_id']) + 1)

                        self.request_upload_response = "success"
                except Exception as e :
                    if st.session_state.DEBUG_ERROR:
                        st.write(e)
                    else :
                        self.request_upload_response = "error"

                
            # Form upload button and response
            if not requestform['error']:
                st.button("Submit 👍",on_click=request_form_submit,key='submit_button',
                        args=[requestform])
            
            if self.request_upload_response !='none':
                if self.request_upload_response =='success':
                    st.success("Successfully submitted")
                else :
                    st.error("Some error occurred")
                self.request_upload_response = 'none'





        # display the summary
        st.markdown("## :blue[my forms]")

        def refresh():
            self._request_db_refresh = True
        st.button("🔃refresh",on_click=refresh,key='download data refresh button')

        dworkbook = self.request_db.copy()
        dworkbook.reset_index(inplace=True,drop=True)

        request_view, timeline_view= st.tabs(["Request View",
                                              "Chronological Order",
                                            #   "Detailed Chronological order"
                                             ])
        # for `request_date` wise view
        view1df = dworkbook.copy()
        view1df = view1df[['timestamp','uniqueid','amount','status']]

        def process_status(status_raw):
            statusdict = json.loads(status_raw)
            if statusdict['status'] == 'pending':
                return 'pending'
            else :
                return f'settled on {statusdict["date_of_paymnt"]}'
            
        view1df['status'] = view1df['status'].apply(lambda x:process_status(x))
        request_view.dataframe(view1df)
        


        # Chronological view calculation
        timeline_array = [['date','amount','department','details','formfilldate','requestid','is_settlement']]
        for _,one_request in dworkbook.iterrows():

            formfilled_time = one_request['timestamp']
            request_id = one_request['uniqueid']
            
            # enter individual payments
            infotable = json.loads(one_request['details'])
            infotable = infotable[1:]
            for one_item in infotable:
                timeline_array.append([*one_item,formfilled_time,request_id,False])
            
            # check for settlement status an add if payment one
            settlement_status = json.loads(one_request['status'])
            # st.write(settlement_status)
            if settlement_status['status'] =='done':
                timeline_array.append([settlement_status['date_of_paymnt'],
                                    -int(settlement_status['amount_of_paymnt']),
                                    'settlement',
                                    settlement_status['paymnt_info'],
                                    settlement_status['date_of_paymnt'],
                                    settlement_status['remark'],
                                    True
                                    ])
        
        timelinedf = pd.DataFrame(timeline_array[1:],columns=timeline_array[0])

        timelinedf.sort_values(by='date',ascending=True,inplace=True)
        timelinedf.index=timelinedf['date']
        timelinedf.drop(columns=['date'],inplace=True)
        balance = [0]
        for amount,is_settlement in zip(timelinedf.amount.tolist(),timelinedf.is_settlement.tolist()):
                balance.append(balance[-1]+int(amount))
        timelinedf.insert(1,"balance",balance[1:])
        timeline_view.dataframe(timelinedf)
        
        dueamount= f'₹ {balance[-1]:,}'
        if balance[-1] > 0:
            st.markdown(f"## :green[You will receive :orange[{dueamount}] from VOICE]")
        elif balance[-1]==0:
            st.markdown("## :green[All Accounts Clear!!!]")
        else :
            st.markdown(f"## :green[Payment of :orange[{dueamount}] is due to VOICE]")
        
        # home completed
    
    def make_payments():
        st.header(":green[Make Payments]")
    def run(self):
        self.subpage_navigator[self.subpage]()

def make_paymnt():
    st.header(":green[Make payments]")
    st.button("settlement form",on_click=change_subpage,args=['default'])

    st.markdown('---')
    def reload():
        if 'all_settlements' in st.session_state:
            st.session_state.pop('all_settlements')
    st.button('🔃refresh',on_click=reload)


    if 'all_settlements' not in st.session_state:
        array = download_data(db_id=1,range_name=SETTLEMENT_INFO)
        temp = pd.DataFrame(array[1:],columns=array[0])
        temp = temp[['actual paymnt date','devotee name','uniqueid','amount','dept','details','any comments','noted_in_expense_sheet','2','settlement_id','status']]
        st.session_state['all_settlements'] = temp.copy()

    workbook = st.session_state['all_settlements']

    # create the total amount summary
    # st.dataframe(workbook)
    workbook['amount'] = workbook['amount'].apply(lambda x: round(float(x),2))

    left,right = st.columns(2)
    view = right.radio('showing',options=['done','pending'],index=1,horizontal=True)
    if view=='done':
        workbook = workbook[workbook.settlement_id !='-1']
    else:
        workbook = workbook[workbook.settlement_id =='-1']

    grouped_summary = workbook[['devotee name','amount']]\
                    .groupby(by='devotee name').agg('sum').reset_index()
    grouped_summary.sort_values(by='amount',ascending=False,inplace=True)
    grouped_summary.index = range(1,1+len(grouped_summary))
    
    left.dataframe(grouped_summary)
    if view=='done':
        right.markdown(f'### :green[Total done: {grouped_summary.amount.sum():,} ₹]')
    elif grouped_summary.amount.sum() >5000:
        right.markdown(f'### :red[Total: {grouped_summary.amount.sum()} ₹]')
    else :
        right.markdown(f'### :green[Total: {grouped_summary.amount.sum()} ₹]')





    st.markdown('---')
    st.markdown("#### :blue[make the payment]")

    devotee = st.radio("Devotees",
    options=sorted(grouped_summary['devotee name'].tolist()),
        label_visibility='hidden',horizontal=True)

    
    # one devotee's summary
    dworkbook = workbook[workbook['devotee name'] == devotee].reset_index()


    def noted_update(range,update_value):
        st.write(f'{REQUEST_SHEET}{range}')
        st.write(update_value)
        response = upload_data(db_id=1,range_name=f'{REQUEST_SHEET}{range}',
                value=[[update_value]])
        # st.write(response)
        if response:
            row  = workbook[workbook['2']==range[1:]].index.tolist()[0]
            st.session_state['all_settlements'].loc[row,'noted_in_expense_sheet']=update_value



    with st.expander("Filters",expanded=True):
        show_list = []  
        filter_status = st.radio("status",options=['pending','staged','completed','all'],horizontal=True,index=0)
        if filter_status =='pending':
            show_list[:] = ['red']
        elif filter_status =='completed':
            show_list[:] = ['green']
        elif filter_status =='staged':
            show_list =['orange']
        elif filter_status =='all':
            show_list[:] = ['red','orange','green']
        
        filter_count = st.slider("show option",min_value=1,
                            max_value=max(2,len(dworkbook)),step=1,value=max(1,len(dworkbook)))




    collection_dict = {'ids':"",'amount':0}
    if filter_status=='staged':
        sachoice = st.radio('select',options=['select all',"select none"],label_visibility='collapsed',index=1)
        if sachoice=='select all':
            checkbox_status = True
        else:
            checkbox_status=False
        
    for r in range(filter_count):        
        title = f"[{1+r}/{len(dworkbook)}] → ₹ :orange[{dworkbook.loc[r,'amount']}] _spent on_ {dworkbook.loc[r,'actual paymnt date']}"
        status = "purple"
        if int(dworkbook.loc[r,'settlement_id']) ==-1:
            if dworkbook.loc[r,'noted_in_expense_sheet'] =='no':
                status = 'red'
            else:
                # noted_in_expense_sheet is 'yes
                status = 'orange'
        else:
            # payment done
            status = 'green'
        if status in show_list:
            st.markdown('---')
            st.write(f"#### :{status}[{title}]")
            
            left,middle,right = st.columns([2,1,1])
            tableinfo = dworkbook.loc[r,'details']
            try :
                tablearray = json.loads(tableinfo)
                tabledf = pd.DataFrame(tablearray[1:],columns=tablearray[0])
                left.dataframe(tabledf)
            except:
                left.markdown(f""":violet[Department: :orange[{dworkbook.loc[r,'dept']}].]
                            :violet[info: :orange[{dworkbook.loc[r,'details']}]]
                """)

            middle.markdown(f":violet[comments: :orange[{dworkbook.loc[r,'any comments']}]]")
            
            # making button for noting in account sheet        
            if status=='red':
                right.button('mark noted',key=f'row{dworkbook.loc[r,"2"]}',
                            on_click=noted_update,
                            args=[f'{NOTED_IN_ACC_COL}{dworkbook.loc[r,"2"]}',
                                'yes'])

            elif status =='orange':
                truthvalue = right.checkbox('select',value=checkbox_status,key=f'row{dworkbook.loc[r,"2"]}')
                if truthvalue:
                    collection_dict['ids'] += dworkbook.loc[r,'uniqueid'] + ','
                    collection_dict['amount'] += float(dworkbook.loc[r,'amount'])
            
            else:
                assert status =='green'
                info = json.loads(dworkbook.loc[r,'status'])
                # right.write(info)
                right.write(f""":violet[settled on :orange[{info["date_of_paymnt"]}].]
                        :violet[had sent total of ₹ :orange[{info["amount_of_paymnt"]}].]
                        :violet[info: :orange[{info['paymnt_info']}].]
                        :violet[remark: :orange[{info['remark']}]]""")
    # st.write(collection_dict)
    st.markdown('---')


    paymnt_dict = {'valid':collection_dict['ids']  != ""}
    
    # st.write(paymnt_dict)
    with st.expander("Make Payment",expanded=True):
         # timestamp
        paymnt_dict['timestamp'] = str(datetime.datetime.now())

        paymnt_dict['request_ids'] = st.text_input(":orange[unique_ids]",
        value=collection_dict['ids'],disabled=True)

        # date of paymnt
        paymnt_date = st.date_input(":green[Date of Payment]")
        paymnt_dict['date_of_paymnt'] = str(paymnt_date)

        paymnt_dict['amount'] = st.number_input('amount',
        value=collection_dict['amount'],disabled=True)

        paymnt_dict['paymnt_info'] = st.text_input(":green[Payment Details]")
        if paymnt_dict['paymnt_info'].strip() =="":
            paymnt_dict['valid'] = (paymnt_dict['valid']) and (True)
        paymnt_dict['remark'] = st.text_area(":orange[any remarks]",height=50)
        # st.write(paymnt_dict)
        if paymnt_dict['valid']:
            def submit(finaldict):
                write_value = []
                for k in PAYMENT_ORDER:
                    write_value.append(finaldict[k])
                response = append_data(db_id=1,range_name=PAYMENT_RANGE,
                value=[write_value])
                # st.write(response)
                if response:
                    collection_dict['amount'] = 0
                    collection_dict['ids'] = ""
                    st.session_state.pop('all_settlements')
            st.button('submit',on_click=submit,args=[paymnt_dict])

