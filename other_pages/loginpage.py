import streamlit as st

# talk to google
from other_pages.googleapi import download_data
import json


class login_Class:
    def __init__(self):
        
        # page map
        self.page_config = {'page_title': "Login Page",
                            'page_icon':'☔',
                            'layout':'centered'}
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
            raw_data = download_data(db_id=1,range_name=self.USER_CREDENTIALS)[0][0]            
            
            # save
            self._userdb = json.loads(raw_data)
            # set refresh to false
            self._userdb_refresh = False
            
        return self._userdb

    @property
    def bdvapp(self):
        return st.session_state.get("bdv_app",None)
    
    def parse_userinfo(self,username):
        """
        uses the userdb to parse userdata for one user (username waalaa)
        returns a dictionary with all the user details
        """
        userdb = {'username':username,**self.userdb[username]}
        try:
            userdb['roles'] = \
            [role.strip() for role in userdb['roles'].replace(" ","").split(",")]
            
            userdb['group'] = \
            [role.strip() for role in userdb['group'].replace(" ","").split(",")]
        except:
            st.error("problem in user data roles or group")
            st.caption("please convey to app maintainer")
            
        return userdb
        
    
    def home(self):
        """ 
        login plus feed also
        """
<<<<<<< HEAD
        login_container = st.empty()
        with login_container.container():
            st.header(":green[Please Login to Continue]")
            default_username = ''
            default_password = ''
            if self.bdvapp.userinfo:
                default_username = self.bdvapp.userinfo['username']
                default_password = self.bdvapp.userinfo['password']
            
            input_user_name = st.text_input("Enter Username",key='username',value=default_username).strip()
            
            input_password = st.text_input("Enter Password",
=======
        st.header(":green[Please Login to Continue]")
        
        default_username = ''
        default_password = ''
        if self.bdvapp.userinfo:
            default_username = self.bdvapp.userinfo['username']
            default_password = self.bdvapp.userinfo['password']
        
        input_user_name = st.text_input("Enter Username",key='username',value=default_username).strip()
        
        input_password = st.text_input("Enter Password",
>>>>>>> 3aa97b7fce5fcb0014a2aaf7e2cdc796188ce13d
                                        type='password',
                                        value=default_password,
                                        key='password').strip()
        
        
<<<<<<< HEAD
=======
        
        
>>>>>>> 3aa97b7fce5fcb0014a2aaf7e2cdc796188ce13d
        ## Verify username and password
        if not input_user_name:
            st.warning("Please Enter Username")
            
        elif not input_password:
            st.warning("Please Enter Password!!")
            
        elif input_user_name in self.userdb.keys():
            
            pswd = self.userdb[input_user_name]['password']
            if input_password == pswd:
                
                # update the title
                login_container.empty()
                with login_container.container():
                    st.header(":rainbow[Jai!! You have logged in]")
                    st.image("./other_pages/images/SSNN_blue.png")
                # get the user details
                self.bdvapp.userinfo = self.parse_userinfo(input_user_name)

                # authenticated
                def takemein(page):
                    self.bdvapp.current_page = page                    
                
                # for all devotees of HG PrGP
                if 'hgprgp_councelle' in self.bdvapp.userinfo['group']:
                    st.markdown('#### :green[Kindly Choose the seva]')
                    st.button("Sadhana Card",on_click=takemein,args=['sadhana_card'])
                
                
                
                # for voice Devotees
                if 'bdv' in self.bdvapp.userinfo['group']:
                    st.markdown('#### :green[How may I serve you?]')
                    left,middle,right = st.columns(3)
                    with left:
                        st.button('Settlements 💸',on_click=takemein,args=['settlement'],key='direct_login_settlement')
                    
                    with middle:
                        st.button("Finder 🔍",on_click=takemein,args=['finder'],key='direct_login_finder')
                    
                    with right:
                        # st.write(user_roles)
                        st.button("Class Notes",on_click=takemein,args=['revision'],key='direct_login_revision')
                        if 'acc_ic' in self.bdvapp.userinfo['roles']:
                            st.button("Accounts 📝",on_click=takemein,args=['dpt_accounts'],key='direct_login_accounts')
                
                
                
                # just for developer
                if self.bdvapp.userinfo['username'] == 'Shiven':
                    st.markdown("#### :orange[Services in progress]")
                    st.button("Article_tagging",on_click=takemein,args=['article_tag'])
                    st.button("Shloka and Songs",on_click=takemein,args=['ssong'])
                    st.button("Hearing Tracker",on_click=takemein,args=['sp_hearing'])

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