import streamlit as st

# talk to google
from other_pages.googleapi import download_data
import json


class login_Class:
    def __init__(self):
        
        # page map
        self.page_map = {
            'home':self.home
        }
        self.current_page = 'home'


        # Sheets related informations
        self.USER_CREDENTIALS = 'credentials!A2'

        # User credentials
        self._userdb = None
        self._userdb_refresh = True

    @property
    def userdb(self):
        """
        1. downloads the data if refresh is True
        2. else returns the database
        Actions
            1. download
            2. save
            3. set the refresh to False
            4. return
        """
        if self._userdb_refresh:
            # refresh the data
            try:
                raw_data = download_data(db_id=1,range_name=self.USER_CREDENTIALS)[0][0]            
                
                # save
                self._userdb = json.loads(raw_data)
                # set refresh to false
                self._userdb_refresh = False
                # return
                return self._userdb
            
            except Exception as e:
                if self.bdvapp.in_development:
                    st.write(e)
                else :
                    st.error("some problem in fetching data")        
        else :
            # refresh not required
            return self._userdb

    @property
    def bdvapp(self):
        return st.session_state.get("bdv_app",None)
    
    def home(self):
        """ 
        Loging page you could say
        """
        st.header(":green[Please Login to Continue]")

        input_user_name = st.text_input("Enter Username",key='username').strip()
        
        input_password = st.text_input("Enter Password",
                                        type='password',
                                        key='password').strip()
        
        ## Verify username and password
        if not input_user_name:
            st.warning("Please Enter Username")
        elif not input_password:
            st.warning("Please Enter Password!!")
        elif input_user_name in self.userdb.keys():
            pswd = self.userdb[input_user_name]['password']
            if input_password == pswd:
                
                # authenticated
                def takemein(page):
                    self.bdvapp.current_page = page
                    self.bdvapp.userinfo = self.userdb[input_user_name]

                    self.bdvapp.userinfo['roles'] = \
                    [role.strip() for role in self.bdvapp.userinfo['roles'].replace(" ","").split(",")]
                
                
                st.button("Login",on_click=takemein,args=['feed'],key='login_button_feed')                
                st.divider()
                st.markdown('#### :green[Direct login to]')


                left,middle,right = st.columns(3)
                with left:
                    st.button('Settlements 💸',on_click=takemein,args=['settlement'],key='direct_login_accounts')
                
                with middle:
                    st.button("Finder 🔍",on_click=takemein,args=['finder'],key='direct_login_finder')
                
                with right:
                    if 'acc_ic' in self.bdvapp.userinfo['roles']:
                        st.button("Accounts 📝",on_click=takemein,args=['dpt_accounts'],key='direct_login_accounts')



            else:
                st.error("Incorrect Password!!")
        else:
            st.warning("Incorrect Username!!")
        
        st.markdown("---")

        st.markdown("""<p><a href="http://wa.me/917260869161?text=Hare%20Krishna%20Pr%20I%20forgot%20my%20password%20please%20">
    <img src="https://icon-library.com/images/change-password-icon/change-password-icon-28.jpg" width="90" height="50">
    </a></p>""",unsafe_allow_html=True)


    def run(self):
        """
        main handler
        """
        self.page_map[self.current_page]()