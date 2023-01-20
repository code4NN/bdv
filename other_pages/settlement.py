import streamlit as st
import datetime
import json
import pandas as pd

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data

# ============= some variables
REQUEST_FORM_ORDER = ['timestamp','date_of_paymnt','name','request_id','amount',
                    'department','agenda','remark']
REQUEST_FORM_RANGE = 'settlement_request!A:H'
SETTLEMENT_INFO = 'settlement_request!A2:M'
REQUEST_SHEET = 'settlement_request!'
NOTED_IN_ACC_COL = 'I'

PAYMENT_ORDER = ['timestamp','date_of_paymnt','amount',
                'paymnt_info','remark','request_ids']
PAYMENT_RANGE = 'settlement_payment!C:H'

# ============= some variables end


## ----------- call back functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage

## -------------
def settlement_form():
    # fetch the relevant data


    # --------------- page
    st.header(" :green[settlement form]")
    if 'acc_ic' in st.session_state['user']['roles']:
        st.button('Make settlement',on_click=change_subpage,args=['make_paymnt'])
    st.markdown('---')
    requestform = {'error':False}
    with st.expander("fill a form",expanded=True):

        # timestamp
        requestform['timestamp'] = str(datetime.datetime.now())

        # date of paymnt
        paymnt_date = st.date_input(":green[Date of Payment]")
        requestform['date_of_paymnt'] = str(paymnt_date)

        # name
        st.write(f":blue[Name: {st.session_state['user']['name']}]")
        requestform['name'] = st.session_state['user']['name']

        # request ID
        requestform['request_id'] = f"{requestform['name']}-{st.session_state['user']['settlement_id']}"

        # amount
        requestform['amount'] = st.number_input(":green[Amount]",min_value=0,
        max_value=10000,step=100)

        # payment for
        requestform['agenda'] = st.text_area(":green[Expense Agenda Details ]",max_chars=500,
                                height=60)
        if not requestform['agenda'].strip():
            st.caption(':red[agenda cannot be blank]')
            requestform['error'] = True

        # department
        requestform['department'] = st.text_input(":green[Department]",max_chars=100)
        if not requestform['department'].strip():
            st.caption(':red[department cannot be blank]')
            requestform['error'] = True

        # any remark

        requestform['remark'] = st.text_area(":orange[any other remark]",height=50,max_chars=300)
        if not requestform['remark'].strip():
            requestform['remark'] ='no comments'
            st.caption(requestform['remark'])

        def submit(requestdict):
            request = []
            for value in REQUEST_FORM_ORDER:
                request.append(requestdict[value])
            request.append('no')
            try:
                response = append_data(db_id=1,range_name=REQUEST_FORM_RANGE,
                    input_type='USER_ENTERED',value=[request])
                if response:
                    st.session_state['successful'] = f':green[successfully filled form for ] :orange[₹ {requestdict["amount"]}]'
                    st.session_state['user']['settlement_id'] = str(int(st.session_state['user']['settlement_id']) + 1)
                    st.session_state.pop('settlement_info')
            except:
                st.session_state['error_upload'] = ':red[some error in uploading data]'
        if not requestform['error']:
            st.button("Submit",on_click=submit,args=[requestform])
        
        if 'error_upload' in st.session_state:
            st.caption(st.session_state['error_upload'])
            st.session_state.pop('error_upload')
        elif 'successful' in st.session_state:
            st.caption(st.session_state['successful'])
            st.session_state.pop('successful')

    st.markdown('---')
    st.markdown("## :blue[my forms]")


    # download the data
    def refresh():
        st.session_state.pop('settlement_info')
    st.button("🔃refresh",on_click=refresh)
    if 'settlement_info' not in st.session_state:
    # if True :
        array = download_data(db_id=1,range_name=SETTLEMENT_INFO)
        temp = pd.DataFrame(array[1:],columns=array[0])
        temp = temp[temp['devotee name']==st.session_state['user']['name']]
        temp = temp[['actual paymnt date','devotee name','uniqueid','amount','dept','details','any comments','noted_in_expense_sheet','2','settlement_id','status']]
        # temp.index = temp['actual paymnt date']
        # temp.reset_index(inplace=True)
        temp['amount'] = temp['amount'].apply(lambda x: int(x))
        st.session_state['settlement_info'] = temp.copy()
    
    dworkbook = st.session_state['settlement_info']
    dworkbook.reset_index(inplace=True,drop=True)
    
    dfsummary = dworkbook.copy()
    dfsummary = dfsummary[['actual paymnt date','uniqueid','amount','dept','details','any comments','settlement_id']]
    dfsummary.rename(columns={'actual paymnt date':'payment date','settlement_id':'status'},inplace=True)
    dfsummary['status'] = dfsummary['status'].apply(lambda x: "done" if x!='-1' else "pending")
    st.dataframe(dfsummary)
    total_sum = dfsummary.amount.sum()
    if total_sum >4000:
        st.markdown(f":red[Total Pending: ₹ {total_sum}]")
    else:
        st.markdown(f":green[Total Pending: ₹ {total_sum}]")

    with st.expander("Filters",expanded=False):
        show_list = []  
        filter_status = st.radio("status",options=['pending','completed','all'],horizontal=True,index=0)
        if filter_status =='pending':
            show_list[:] = ['red','orange']
        elif filter_status =='completed':
            show_list[:] = ['green']
        elif filter_status =='all':
            show_list[:] = ['red','orange','green']        
        
        filter_count = st.slider("show option",min_value=1,
                            max_value=(len(dworkbook)),step=1,value=len(dworkbook))
        



    
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
            
            left,middle,right = st.columns(3)
            left.markdown(f""":violet[Department: :orange[{dworkbook.loc[r,'dept']}].]
                        :violet[info: :orange[{dworkbook.loc[r,'details']}]]
            """)

            middle.markdown(f":violet[comments: :orange[{dworkbook.loc[r,'any comments']}]]")
            
            # making button for noting in account sheet        
            if status=='green':
                info = json.loads(dworkbook.loc[r,'status'])
                # right.write(info)
                right.write(f""":violet[settled on :orange[{info["date_of_paymnt"]}].]
                        :violet[had sent total of ₹ :orange[{info["amount_of_paymnt"]}].]
                        :violet[info: :orange[{info['paymnt_info']}].]
                        :violet[remark: :orange[{info['remark']}]]""")
            elif status =="red":
                right.write(":orange[settlement progress yet to begin]")
            elif status =='orange':
                right.write(":orange[expense has been noted. Payment will be done soon]")

    st.markdown('---')
    st.button("feed",on_click=change_page,args=['feed'])



    # other status


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
        # temp = temp[temp['devotee name']==st.session_state['user']['name']]
        temp = temp[['actual paymnt date','devotee name','uniqueid','amount','dept','details','any comments','noted_in_expense_sheet','2','settlement_id','status']]
        # temp.index = temp['actual paymnt date']
        st.session_state['all_settlements'] = temp.copy()

    workbook = st.session_state['all_settlements']

    # create the total amount summary
    workbook['amount'] = workbook['amount'].apply(lambda x: round(float(x),2))
    grouped_summary = workbook[['devotee name','amount']]\
                    .groupby(by='devotee name').agg('sum').reset_index()
    grouped_summary.sort_values(by='amount',ascending=False,inplace=True)
    grouped_summary.index = range(1,1+len(grouped_summary))
    
    left,right = st.columns(2)
    left.dataframe(grouped_summary)
    if grouped_summary.amount.sum() >5000:
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



    with st.expander("Filters",expanded=False):
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
                            max_value=(len(dworkbook)),step=1,value=len(dworkbook))




    collection_dict = {'ids':"",'amount':0}    
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
            
            left,middle,right = st.columns(3)
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
                truthvalue = right.checkbox('select',value=False,key=f'row{dworkbook.loc[r,"2"]}')
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
    with st.expander("Make Payment",expanded=False):
         # timestamp
        paymnt_dict['timestamp'] = str(datetime.datetime.now())

        paymnt_dict['request_ids'] = st.text_input(":orange[unique_ids]",
        value=collection_dict['ids'][:-1],disabled=True)

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
                value=[write_value],input_type='USER_ENTERED')
                # st.write(response)
                if response:
                    collection_dict['amount'] = 0
                    collection_dict['ids'] = ""
                    st.session_state.pop('all_settlements')
            st.button('submit',on_click=submit,args=[paymnt_dict])


# -------------- Wrapper
login_state_map = {'default':settlement_form,
                    'make_paymnt':make_paymnt}

def settlement_main():
    if 'substate' not in st.session_state:
        # default behaviour
        login_state_map['default']()

    elif st.session_state['substate'] in login_state_map.keys():
        # directed behaviour
        login_state_map[st.session_state['substate']]()
    else:
        # exceptional
        login_state_map['default']()        