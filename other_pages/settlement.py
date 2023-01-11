import streamlit as st
import datetime
import json

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
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

    st.markdown('---')
    requestform = {}
    with st.expander("fill a form",expanded=False):
        # name
        st.write(f":blue[Name: {st.session_state['user']['name']}]")
        requestform['name'] = st.session_state['user']['name']

        # timestamp
        requestform['timestamp'] = str(datetime.datetime.now())

        # date of paymnt
        paymnt_date = st.date_input(":green[Date of Payment]")
        requestform['date_of_paymnt'] = str(paymnt_date)

        # request ID


        # amount
        requestform['amount'] = st.number_input(":green[Amount]",min_value=0,
        max_value=10000,step=100)

        # payment for

        requestform['agenda'] = st.text_area(":green[Expense Agenda Details ]",max_chars=500,
                                height=60)

        # department
        requestform['department'] = st.text_input(":green[Department]",max_chars=100)

        # any remark

        requestform['remark'] = st.text_area(":orange[any other remark]",height=50,max_chars=300)
    
        st.button("Submit")
# -------------- Wrapper
login_state_map = {'default':settlement_form}

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