import streamlit as st
import json
import time
from other_pages.googleapi import fetch_data
from other_pages.googleapi import fetch_data_forced
from other_pages.googleapi import update_range

from other_pages.googleapi import append_range

def change_subpage(subpage):
    st.session_state['substate'] = subpage

def user_login():
    usercreds = st.secrets['credentials']
    usersinfo = None
    if 'userinfo' in st.session_state:
        usersinfo = st.session_state['userinfo']
    else:
        users = fetch_data(usercreds['sheetID'],usercreds['range'])[0][0]    
        usersinfo = json.loads(users)
    
    st.header(":green[Please Login to Continue]")
    st.text_input("Enter Username",key='username')
    st.text_input("Enter Password",
                    type='password',
                    key='password')
    def login():
    # verify username
        if st.session_state['username'] == 'register' and \
           st.session_state['password'] == 'gaur':
           st.session_state['substate'] = 'register'

        if st.session_state['username'] in usersinfo.keys():
            pswd = usersinfo[st.session_state['username']]['password']
            if st.session_state['password'] == pswd:
                # verified
                st.session_state['state'] = 'feed'
                st.session_state['user'] = usersinfo[st.session_state['username']]
                
                
            
    st.button("Login",on_click=login)
    


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

    st.subheader(':blue[Step 1]')
    username = st.text_input("Enter Username")
    usercreds = st.secrets['credentials']    
    users = fetch_data(usercreds['sheetID'],usercreds['range'])[0][0]

    usersinfo = json.loads(users)
    if username in usersinfo.keys():
        st.markdown(':red[Username already Taken!!]')
    elif username !="":
        st.markdown(':green[Username available]')
        
        def userapply(username):
            if 'applied' in st.session_state and username in st.session_state['applied'] :
                st.markdown("# :red[Haribol Pr!!, You have already applied]")
            else:
                sheetid = usercreds['sheetID']
                range = 'registration!A:A'
                append_range(sheetid,range,[[username]])
                st.session_state['applied'] = username
                st.markdown(":green[Your request Submitted !!]")

        st.button('Submit',on_click=userapply,args=[username])

    st.markdown('---')
    step2 = {'submitted':False}
    
    st.subheader(':blue[Step 2]')
    st.caption("With name and pin")
    step2['username'] = st.text_input("Enter username",key='user2')
    step2['pin'] = st.text_input("Enter pin",key='pin2')
    step2['pass1'] = st.text_input("Enter new password",key='pass1')
    step2['pass2'] = st.text_input("Confirm password",key='confirm_pass2')

    status = st.radio("Completed",options=['not','yes'],horizontal=True)
    step2['submitted'] = status == 'yes'
    if step2['submitted']:

        if step2['username'] =="":
            st.write(":red[enter username]")
        else:
            usercreds = st.secrets['credentials']
            reg_status = fetch_data(usercreds['sheetID'],'credentials!C2')[0][0]
            reg_status = json.loads(reg_status)
            st.session_state['reguser'] = {'userid':step2['username'],
                                            'name':reg_status[step2['username']]['name'],
                                            'group':reg_status[step2['username']]['group'],
                                            'password':step2['pass1']
                                            }
            if step2['pin'] =="":
                st.write(":red[enter pin]")
            elif step2['pin'] != reg_status[step2['username']]['pin']:
                st.write(step2['pin'])
                st.write(reg_status[step2['username']]['pin'])
                st.write(":red[wrong pin]")
            elif step2['pass1'] =="":
                st.write(":red[enter password]")
            elif step2['pass1'] != step2['pass2']:
                st.write(":red[password does not match]")
            else:
                
                if step2['username'] in reg_status.keys():
                    if step2['pin'] == reg_status[step2['username']]['pin']:
                        # show the submit button
                        def First_Login():

                            reginfo = st.session_state['reguser']
                            creds = st.secrets['credentials']
                            db_accounts = fetch_data_forced(creds['sheetID'],creds['range'])[0][0]
                            db_accounts = json.loads(db_accounts)
                            if step2['username'] in db_accounts.keys():
                                st.write(":green[Your account created already]")
                                st.caption("please contact for moreinfo")
                            else:
                                new_db_accounts = {**db_accounts,
                                                    **{reginfo['userid']:{'name':reginfo['name'],
                                                                                        'password':reginfo['password'],
                                                                                        'group':reginfo['group']}
                                                        }
                                                    }
                                new_db_accounts = json.dumps(new_db_accounts,sort_keys=True)
                                response = update_range(creds['sheetID'],
                                                        creds['range'],
                                                        [[new_db_accounts]])
                                verify = json.loads(response['values'][0][0])
                                if step2['username'] in verify.keys():
                                    st.session_state['reg_response'] = True
                                else:
                                    st.session_state['reg_response'] = False
                            # st.write(db_accounts)
                            # st.write(new_db_accounts)


                        st.button("Create Account",on_click=First_Login)
                        if 'reg_response' not in st.session_state:
                            pass
                        elif st.session_state['reg_response']:
                            st.write(":green[Account created successfully!!]")
                            def gotomain():
                                st.session_state['substate'] = 'default'
                                # update userinfo
                                usercreds = st.secrets['credentials']
                                users = fetch_data_forced(usercreds['sheetID'],usercreds['range'])[0][0]    
                                usersinfo = json.loads(users)
                                st.session_state['usersinfo'] = usersinfo
                            st.button("Go to login",on_click=gotomain)
                        else:
                            st.write(":red[Some api error]")
                else:
                    st.write(":red[invalid username]")

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