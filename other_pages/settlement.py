import streamlit as st
import datetime
import json

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data

# ============= some variables
REQUEST_FORM_ORDER = ['timestamp','date_of_paymnt','name','request_id','amount',
                    'department','agenda','remark']
REQUEST_FORM_RANGE = 'settlement_request!A:H'

PAYMENT_ORDER = ['timestamp','date_of_paymnt','amount',
                'paymnt_info','remakr','request_ids']
PAYMENT_RANGE = 'settlement_paymnt!B:G'
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
    with st.expander("fill a form",expanded=False):

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
        if requestform['agenda'] =="":
            st.caption(':red[agenda cannot be blank]')
            requestform['error'] = True

        # department
        requestform['department'] = st.text_input(":green[Department]",max_chars=100)
        if requestform['department'] =="":
            st.caption(':red[department cannot be blank]')
            requestform['error'] = True

        # any remark

        requestform['remark'] = st.text_area(":orange[any other remark]",height=50,max_chars=300)
        
        def submit(requestdict):
            request = []
            for value in REQUEST_FORM_ORDER:
                request.append(requestdict[value])
            request.append('no')
            try:
                response = append_data(db_id=1,range_name=REQUEST_FORM_RANGE,
                        input_type='USER_ENTERED',value=[request])
                if response:
                    st.session_state['successful'] = ':green[successful]'
                    st.session_state['user']['settlement_id'] = str(int(st.session_state['user']['settlement_id']) + 1)
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


def make_paymnt():
    st.header(":green[Make payments]")
    st.button("settlement form",on_click=change_subpage,args=['default'])

    st.markdown('---')
    paymnt_dict = {}

    with st.expander("Make Payment",expanded=True):
         # timestamp
        paymnt_dict['timestamp'] = str(datetime.datetime.now())

        paymnt_dict['request_ids'] = st.text_input(":green[ids]")

        # date of paymnt
        paymnt_date = st.date_input(":green[Date of Payment]")
        paymnt_dict['date_of_paymnt'] = str(paymnt_date)

        paymnt_dict['amount'] = st.number_input('amount ')

        paymnt_dict['paymnt_info'] = st.text_input(":green[Payment Details]")

        paymnt_dict['remark'] = st.text_area(":orange[any remarks]",height=50)
        


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