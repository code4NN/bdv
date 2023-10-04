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
        self._userdb = {"ssNN":{"password":"gaur","name":"Sample","roles":"","group":"nak","settlement_id":"3"},"Pragyesh":{"password":"nimai","name":"Pragyesh","roles":"","group":"nak","settlement_id":"3"},"Dhruv":{"password":"DddD","name":"Dhruv","roles":"","group":"nak","settlement_id":"61"},"harsh":{"password":"harsh098","name":"Harsh","roles":"","group":"nak","settlement_id":"5"},"Jateen":{"password":"Harii","name":"Jateen","roles":"","group":"yud","settlement_id":"33"},"Shridhar":{"password":"6789","name":"Shridhar","roles":"","group":"yud","settlement_id":"5"},"Akash":{"password":"akash@2254","name":"Akash","roles":"search++","group":"yud","settlement_id":"3"},"Satyam":{"password":"Bittu@09","name":"Satyam","roles":"","group":"yud","settlement_id":"14"},"Shiven":{"password":"trinadapi","name":"Shivendra","roles":"acc_ic,search++","group":"yud","settlement_id":"40"},"trideep":{"password":"Gopal","name":"Trideep","roles":"","group":"yud","settlement_id":"4"},"Parth":{"password":"parth@123","name":"Parth","roles":"","group":"yud","settlement_id":"1"},"dchandak":{"password":"cc108","name":"Devansh","roles":"","group":"yud","settlement_id":"6"}}        
        self._userdb_refresh = False

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
                if st.session_state['DEBUG_ERROR']:
                    st.write(e)
                else :
                    st.error("some problem in fetching data")        
        else :
            # refresh not required
            return self._userdb

    def home(self):
        """ 
        This is the landing page
        Loging page you could say
        """
        st.header(":green[Please Login to Continue]")

        input_user_name = st.text_input("Enter Username",key='username')
        
        if input_user_name.__contains__(" "):
            st.markdown(':red[Haribol, remove space from username]')

        input_password = st.text_input("Enter Password",
                                        type='password',
                                        key='password')
        
            
        ## Verify username and password
        if input_user_name in self.userdb.keys():
            pswd = self.userdb[input_user_name]['password']
            if input_password == pswd:
                
                # authenticated
                def takemein(page):
                    st.session_state['_page'] = page
                    st.session_state['_user_account_info'] = self.userdb[input_user_name]

                    st.session_state['_user_account_info']['roles'] = \
                    st.session_state['_user_account_info']['roles'].replace(" ","").split(",")
                
                st.button("Login",on_click=takemein,args=['feed'],key='login_button_feed')
                
                st.markdown('---')
                st.markdown('#### :green[Direct login to]')

                left,middle,right = st.columns(3)
                left.button('Settlements 💸',on_click=takemein,args=['accounts'],key='direct_login_accounts')
        st.markdown("---")

        st.markdown("""<p><a href="http://wa.me/917260869161?text=Hare%20Krishna%20Pr%20I%20forgot%20my%20password%20please%20">
    <img src="https://icon-library.com/images/change-password-icon/change-password-icon-28.jpg" width="90" height="50">
    </a></p>""",unsafe_allow_html=True)


    def run(self):
        """
        main handler
        """
        self.subpage_navigator[self.subpage]()