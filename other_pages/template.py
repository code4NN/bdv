import streamlit as st
import json
import time
from other_pages.googleapi import fetch_data
from other_pages.googleapi import fetch_data_forced
from other_pages.googleapi import update_range

from other_pages.googleapi import append_range

def change_subpage(subpage):
    st.session_state['substate'] = subpage

# ---------------------- Wrapper
# login_state_map = {'':}

# def login_main():
#     if 'substate' not in st.session_state:
#         # default behaviour
#         user_login()

#     elif st.session_state['substate'] in login_state_map.keys():
#         # directed behaviour
#         login_state_map[st.session_state['substate']]()
#     else:
#         # exceptional
#         user_login()        