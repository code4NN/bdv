import streamlit as st
import json
from other_pages.googleapi import fetch_data


def user_login():
    usercreds = st.secrets['credentials']
    users = fetch_data(usercreds['sheetID'],usercreds['range'])[0][0]
    
    usersinfo = json.loads(users)
    
    st.header(":green[Please Login to Continue]")
    st.text_input("Enter Username",key='username')
    st.text_input("Enter Password",
                    type='password',
                    key='password')
    def login():
    # verify username
        if st.session_state['username'] in usersinfo.keys():
            pswd = usersinfo[st.session_state['username']]            
            if st.session_state['password'] == pswd:
                # verified
                st.session_state['state'] = 'feed'
            
    st.button("Login",on_click=login)
    #========== devlop

# ---------------------- Wrapper
login_state_map = {'default':user_login,
                   }

def login_main():
    if 'substate' not in st.session_state:
        # default behaviour
        user_login()

    elif st.session_state['substate'] in login_state_map.keys():
        # directed behaviour
        login_state_map[st.session_state['substate']]()
    else:
        # exceptional
        user_login()
        