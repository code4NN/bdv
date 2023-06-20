import streamlit as st
# talk to google
from other_pages.googleapi import download_data
import json


class page4_login:
    def __init__(self):
        
        self.subpage = 'home'
        self.subpage_navigator = {
            'home':self.home
        }

        # Sheets related informations
        self.USER_CREDENTIALS = 'credentials!A2'

        # various databases
        self.userdb = None
        self.load_user_data()

    def load_user_data(self):
        """
        Download the user credentials
        """
        try:
            raw_data = download_data(db_id=1,range_name=self.USER_CREDENTIALS)[0][0]            
            self.userdb = json.loads(raw_data)

        except Exception as e:
            if st.session_state['DEBUG_ERROR']:
                st.write(e)
            st.error("some problem in fetching data")

    def home(self):
        """ 
        This is the landing page
        Loging page you could say
        """
        st.header(":green[Please Login to Continue]")

        input_user = st.text_input("Enter Username",key='username')
        if input_user.__contains__(" "):
            st.caption(':red[Haribol, remove space from username]')

        input_password = st.text_input("Enter Password",
                            type='password',
                            key='password')
        
            
        ## Verify username and password
        if input_user in self.userdb.keys():
            pswd = self.userdb[input_user]['password']
            if input_password == pswd:
                # verified
                def takemein(page):
                    st.session_state['state'] = page
                    st.session_state['user'] = self.userdb[input_user]
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


    def run(self):
        self.subpage_navigator[self.subpage]()

# ------------------------ some Constants
# ------------------------ /some Constants

# ======================== some functions
def change_subpage(subpage):
    st.session_state['substate'] = subpage
# ======================== some functions end

def user_login():
    
    # load the account details
    if 'all_user_data' not in st.session_state:
        
            
    
    all_user_data = st.session_state['all_user_data']
        
    
    
    # -------------------------------LOGIN PAGE
    

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