import streamlit as st
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
# ---------------------- Wrapper
login_state_map = {}

def login_main():
    if 'substate' not in st.session_state:
        # default behaviour
        pass

    elif st.session_state['substate'] in login_state_map.keys():
        # directed behaviour
        login_state_map[st.session_state['substate']]()
    else:
        # exceptional
        pass 