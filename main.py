import streamlit as st

# Import various classes
from other_pages.loginpage import login_Class
from other_pages.feed import feed_Class
from other_pages.settlement import settlement_Class
from other_pages.finder import finder_Class
from other_pages.accounts import account_Class
from other_pages.hearing_tracker import hearing_Class



class myapp:
    def __init__(self,in_development,requires_login):

        # Global parameters
        self.in_development = in_development
        self.requires_login = requires_login
        self.development_page = ''

        # register all the page
        self.page_map = {'login':login_Class(),
                         'feed':feed_Class(),
                         'settlement':settlement_Class(),
                         'finder': finder_Class(),
                         'dpt_accounts': account_Class(),
                         'hearing_tracker': hearing_Class()
                          }
        # landing page
        self.current_page = 'login'
        
        # User related data
        # Get's populated after login
        self.userinfo = None
    
    @property
    def page_config(self):
        if self.in_development and self.requires_login:
            if self.userinfo:
                return self.page_map[self.development_page].page_config
            else:
                return self.page_map['login'].page_config
        else:
            return self.page_map[self.current_page].page_config

    def run(self):
        # check if dev or prod
        if self.in_development:
            # dev > check if we need to login
            if self.requires_login:
                # needs login > Now check if user have logged in
                
                if self.userinfo is None:
                    # user have not logged in >> land to login page
                    self.page_map[self.current_page].run()
                else:
                    # land to developer page if it does not need login
                    self.page_map[self.development_page].run()
            else:
                # does not need login > directly run developer page
                self.page_map[self.development_page].run()

        # in production
        else:
            self.page_map[self.current_page].run()

# End of My App Class



# Create an instance of the voice-app
if 'bdv_app' not in st.session_state:
    if st.secrets['developer']['in_development']==1:
        if st.secrets['developer']['requires_login']==1:
            st.session_state['bdv_app'] = myapp(in_development=True,
                                                requires_login=True)
        else :
            st.session_state['bdv_app'] = myapp(in_development=True,
                                                requires_login=False)
    else:
        st.session_state['bdv_app'] = myapp(in_development=False,requires_login=False)





# For development
main_app = st.session_state['bdv_app']
if main_app.in_development:
    PAGE_DEVELOPING = 'settlement'
    PAGE_CLASS = settlement_Class()
    SUB_PAGE_DEVELOPING = 'mysite'


    # tell which is my developement class
    main_app.development_page = PAGE_DEVELOPING
    # Set the subpage
    PAGE_CLASS.current_page = SUB_PAGE_DEVELOPING
    # update the page_map
    main_app.page_map[PAGE_DEVELOPING] = PAGE_CLASS


st.set_page_config(**main_app.page_config)





try:
    main_app.run()

except Exception as e:
    st.error("Haribol!! Got some error")

    if main_app.in_development:
        st.write(e)
    if main_app.userinfo:
        if 'dev' in main_app.userinfo['roles']:
            st.write(e)

# st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")