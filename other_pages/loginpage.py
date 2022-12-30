import streamlit as st
import json
from other_pages.googleapi import fetch_data
from other_pages.googleapi import update_range

def change_subpage(subpage):
    st.session_state['substate'] = subpage

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
    st.button("New Registration",on_click=change_subpage,args=['register'])


def registration():
    # to register a new user
    st.header(":green[Hare Krishna]")
    st.subheader(":blue[New User Registration]")
    with st.expander("Steps for registratino",expanded=True):
        st.markdown("## Steps")
        st.markdown("1. Enter a username that has not been used before")
        st.markdown("2. After submit, you will need to collect a four digit PIN from respective devotee")
        st.markdown(" :blue[With four digit pin you can set the password]")
        
        st.markdown(':green[Then usual login]')

    username = st.text_input("Enter Username")
    usercreds = st.secrets['credentials']
    users = fetch_data(usercreds['sheetID'],usercreds['range'])[0][0]
    usersinfo = json.loads(users)
    if username in usersinfo.keys():
        st.markdown(':red[Username already Taken!!]')
    elif username !="":
        st.markdown(':green[Username available]')
        
        def userapply(username):
            sheetid = usercreds['sheetID']
            range = 'credentials!C3'
            update_range(sheetid,range,[[username]])
            
            st.markdown(":green[Your request Submitted !!]")
            st.session_state.pop("substate")

        st.button('Submit',on_click=userapply,args=[username])





# ---------------------- Wrapper
login_state_map = {'default':user_login,
                   'register':registration}

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