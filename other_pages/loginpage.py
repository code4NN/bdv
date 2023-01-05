# Some imports
import streamlit as st

# talk to google
from other_pages.googleapi import upload_data
from other_pages.googleapi import download_data
import json

# ------------------------ some Constants
USER_CREDENTIALS = 'credentials!A2'
# ------------------------ some Constants end

# ======================== some functions
def change_subpage(subpage):
    st.session_state['substate'] = subpage
# ======================== some functions end

def user_login():
    
    # load the account details
    if 'all_user_data' not in st.session_state:
        try:
            raw_data = download_data(db_id=1,range_name=USER_CREDENTIALS)[0][0]            
            st.session_state['all_user_data'] = json.loads(raw_data)
        except:
            st.error("some problem in fetching data")
            st.write(":blue[ensure you are connected to internet]")
            st.write("please close the tab and open a new one")
            return None
    
    all_user_data = st.session_state['all_user_data']
        
    
    
    # -------------------------------LOGIN PAGE
    st.header(":green[Please Login to Continue]")
    input_user = st.text_input("Enter Username",key='username')
    input_password = st.text_input("Enter Password",
                        type='password',
                        key='password')
    
    
    if input_user in all_user_data.keys():
        pswd = all_user_data[input_user]['password']
        if input_password == pswd:
            # verified
            def takemein(page):
                st.session_state['state'] = page
                st.session_state['user'] = all_user_data[input_user]
            
            st.button("Login",on_click=takemein,args=['feed'],key='feed')
            
            st.markdown('---')
            st.markdown('#### :green[Direct login to]')
            st.button('Sadhana Card',on_click=takemein,args=['Sadhana_Card'],key='sc')
            st.button('bdv departments',on_click=takemein,args=['dept_structure'],key='dept')



# def registration():
#     # to register a new user
#     st.header(":green[Hare Krishna]")
#     st.subheader(":blue[New User Registration]")
#     with st.expander("Steps for registratino",expanded=True):
#         st.markdown("## Steps")
#         st.markdown("1. Enter a username that has not been used before")
#         st.markdown("2. After submit, you will need to collect a four digit PIN from respective devotee")
#         st.markdown(" :blue[With four digit pin you can set the password]")
        
#         st.markdown(':green[Then usual login]')

#     st.subheader(':blue[Step 1]')
#     username = st.text_input("Enter Username")
#     usercreds = st.secrets['credentials']    
#     users = fetch_data(usercreds['sheetID'],usercreds['range'])[0][0]

#     usersinfo = json.loads(users)
#     if username in usersinfo.keys():
#         st.markdown(':red[Username already Taken!!]')
#     elif username !="":
#         st.markdown(':green[Username available]')
        
#         def userapply(username):
#             if 'applied' in st.session_state and username in st.session_state['applied'] :
#                 st.session_state['resubmitform'] = "# :red[Haribol Pr!!, You have already applied]"
#             else:
#                 sheetid = usercreds['sheetID']
#                 range = 'registration!A:A'
#                 append_range(sheetid,range,[[username]])
#                 st.session_state['applied'] = username
#                 st.session_state['confirm_submission'] =":green[Your request Submitted !!]"


#         st.button('Submit',on_click=userapply,args=[username])
#         if 'resubmitform' in st.session_state:
#             st.markdown(st.session_state['resubmitform'])
#             st.session_state.pop('resubmitform')
#         if 'confirm_submission' in st.session_state:
#             st.markdown(st.session_state['confirm_submission'])
#             st.session_state.pop('confirm_submission')
#     st.markdown('---')
#     step2 = {'submitted':False}
    
#     st.subheader(':blue[Step 2]')
#     st.caption("With name and pin")
#     step2['username'] = st.text_input("Enter username",key='user2')
#     step2['pin'] = st.text_input("Enter pin",key='pin2')
#     step2['pass1'] = st.text_input("Enter new password",key='pass1')
#     step2['pass2'] = st.text_input("Confirm password",key='confirm_pass2')

#     status = st.radio("Completed",options=['not','yes'],horizontal=True)
#     step2['submitted'] = status == 'yes'
#     if step2['submitted']:

#         if step2['username'] =="":
#             st.write(":red[enter username]")
#         else:
#             usercreds = st.secrets['credentials']
#             reg_status = fetch_data(usercreds['sheetID'],'credentials!C2')[0][0]
#             reg_status = json.loads(reg_status)
#             st.session_state['reguser'] = {'userid':step2['username'],
#                                             'name':reg_status[step2['username']]['name'],
#                                             'group':reg_status[step2['username']]['group'],
#                                             'password':step2['pass1']
#                                             }
#             if step2['pin'] =="":
#                 st.write(":red[enter pin]")
#             elif step2['pin'] != reg_status[step2['username']]['pin']:
#                 st.write(step2['pin'])
#                 st.write(reg_status[step2['username']]['pin'])
#                 st.write(":red[wrong pin]")
#             elif step2['pass1'] =="":
#                 st.write(":red[enter password]")
#             elif step2['pass1'] != step2['pass2']:
#                 st.write(":red[password does not match]")
#             else:
                
#                 if step2['username'] in reg_status.keys():
#                     if step2['pin'] == reg_status[step2['username']]['pin']:
#                         # show the submit button
#                         def First_Login():

#                             reginfo = st.session_state['reguser']
#                             creds = st.secrets['credentials']
#                             db_accounts = fetch_data_forced(creds['sheetID'],creds['range'])[0][0]
#                             db_accounts = json.loads(db_accounts)
#                             if step2['username'] in db_accounts.keys():
#                                 st.write(":green[Your account created already]")
#                                 st.caption("please contact for moreinfo")
#                             else:
#                                 new_db_accounts = {**db_accounts,
#                                                     **{reginfo['userid']:{'name':reginfo['name'],
#                                                                                         'password':reginfo['password'],
#                                                                                         'group':reginfo['group']}
#                                                         }
#                                                     }
#                                 new_db_accounts = json.dumps(new_db_accounts,sort_keys=True)
#                                 response = update_range(creds['sheetID'],
#                                                         creds['range'],
#                                                         [[new_db_accounts]])
#                                 verify = json.loads(response['values'][0][0])
#                                 if step2['username'] in verify.keys():
#                                     st.session_state['reg_response'] = True
#                                 else:
#                                     st.session_state['reg_response'] = False
#                             # st.write(db_accounts)
#                             # st.write(new_db_accounts)


#                         st.button("Create Account",on_click=First_Login)
#                         if 'reg_response' not in st.session_state:
#                             pass
#                         elif st.session_state['reg_response']:
#                             st.write(":green[Account created successfully!!]")
#                             def gotomain():
#                                 st.session_state['substate'] = 'default'
#                                 # update userinfo
#                                 usercreds = st.secrets['credentials']
#                                 users = fetch_data_forced(usercreds['sheetID'],usercreds['range'])[0][0]    
#                                 usersinfo = json.loads(users)
#                                 st.session_state['usersinfo'] = usersinfo
#                             st.button("Go to login",on_click=gotomain)
#                         else:
#                             st.write(":red[Some api error]")
#                 else:
#                     st.write(":red[invalid username]")

# ---------------------- Wrapper
view_dict= {'default':user_login}

def login_main():    
    if 'substate' not in st.session_state:
        # default behaviour
        view_dict['default']()
    else:
        view = st.session_state['substate']
        if view in view_dict.keys():
            # directed behaviour
            view_dict[view]()
        else:
            # exceptional     
            view_dict['default']()