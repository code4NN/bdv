import streamlit as st
# talk to google
from other_pages.googleapi import download_data
import json

# ------------------------ some Constants
USER_CREDENTIALS = 'credentials!A2'
# ------------------------ /some Constants

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
        except Exception as e:
            if st.session_state['DEBUG_ERROR']:
                st.write(e)
            st.error("some problem in fetching data")
            
    
    all_user_data = st.session_state['all_user_data']
        
    
    
    # -------------------------------LOGIN PAGE
    st.header(":green[Please Login to Continue]")
    input_user = st.text_input("Enter Username",key='username')
    if input_user.__contains__(" "):
        st.caption(':red[Haribol, remove space from username]')
    input_password = st.text_input("Enter Password",
                        type='password',
                        key='password')
    
        
    ## Verify username and password
    if input_user in all_user_data.keys():
        pswd = all_user_data[input_user]['password']
        if input_password == pswd:
            # verified
            def takemein(page):
                st.session_state['state'] = page
                st.session_state['user'] = all_user_data[input_user]
                st.session_state['user']['roles'] = st.session_state['user']['roles'].split(",")
            
            st.button("Login",on_click=takemein,args=['feed'],key='feed')
            
            st.markdown('---')
            st.markdown('#### :green[Direct login to]')

            left,middle,right = st.columns(3)
            left.button('Sadhana Card',on_click=takemein,args=['Sadhana_Card'],key='sc')
            middle.button('💸 settlement',on_click=takemein,args=['settlement'],key='acc')
            right.button('bdv departments',on_click=takemein,args=['dept_structure'],key='dept')
    st.markdown("---")
    st.markdown("""<p><a href="http://wa.me/917260869161?text=Hare%20Krishna%20Pr%20I%20forgot%20my%20password%20please%20">
<img src="https://icon-library.com/images/change-password-icon/change-password-icon-28.jpg" width="90" height="50">
</a></p>""",unsafe_allow_html=True)


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