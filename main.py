import streamlit as st

# Import various classes
from other_pages.loginpage import login_Class
from other_pages.feed import feed_Class
from other_pages.sadhana_card import sadhana_card_class
from other_pages.settlement import settlement_Class
from other_pages.accounts import account_Class
from other_pages.hearing_tracker import hearing_Class
from other_pages.lecture_notes import class_notes_Class
from other_pages.thematic_encyclopaedia import sskkb



class myapp:
    def __init__(self,in_development,requires_login):

        # Global parameters
        self.in_development = in_development
        self.requires_login = requires_login
        self.development_page = ''

        # register all the page
        self.page_map = {'login':login_Class(),
                         'feed':feed_Class(),
                         'sadhana_card':sadhana_card_class(),
                         'settlement':settlement_Class(),
                         'dpt_accounts': account_Class(),
                         'heart_medicine': hearing_Class(),
                         'revision': class_notes_Class(),
                         'article_tag':sskkb()
                          }
        # landing page
        self.current_page = 'login'
        
        # query parameters
        self.query_template = {'landing_page':'to',
                             'username':'user',
                             'password':'pass'}
        self.handled_query_params = False
        
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
            
            # handling query parameters
            # st.write(st.query_params)
            if not self.handled_query_params:
                query_params = st.query_params
                
                # for username and password
                if self.query_template['username'] in query_params.keys() and \
                    self.query_template['password'] in query_params.keys():
                    username = query_params[self.query_template['username']]
                    password = query_params[self.query_template['password']]
                    
                    login_page = self.page_map['login']
                    userdb = login_page.userdb

                    if username in userdb.keys():
                        if password == userdb[username]['password']:
                            # success
                            self.userinfo = {'username':username,**userdb[username]}
                            try:
                                    self.userinfo['roles'] = \
                                    [role.strip() for role in self.userinfo['roles'].replace(" ","").split(",")]
                                    self.userinfo['group'] = \
                                    [role.strip() for role in self.userinfo['group'].replace(" ","").split(",")]
                            except:
                                    self.userinfo['roles'] = ['some_error']
                                    self.userinfo['group'] = ['some_error']
                
                            # now allow access based on user access
                            if self.query_template['landing_page'] in query_params.keys():
                                
                                # for sadhana card ?to=sc
                                if query_params[self.query_template['landing_page']] == 'sc':
                                    # prabhuji wants to go to sadhana card
                                    # check if he have the access
                                    if 'hgprgp_councelle' in self.userinfo['group']:
                                        # allows access
                                        self.current_page = 'sadhana_card'
                
                st.query_params.clear()
                self.handled_query_params = True
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
    PAGE_DEVELOPING = 'finder'
    PAGE_CLASS = finder_Class()
    SUB_PAGE_DEVELOPING = 'other'


    # tell which is my developement class
    main_app.development_page = PAGE_DEVELOPING
    # Set the subpage
    PAGE_CLASS.current_page = SUB_PAGE_DEVELOPING
    # update the page_map
    main_app.page_map[PAGE_DEVELOPING] = PAGE_CLASS


st.set_page_config(**main_app.page_config)





try:
    if not main_app.in_development:
        st.markdown(
        """
        <style>
        [data-testid="baseButton-header"] {
            visibility: hidden;
        }
        [data-testid="stHeader"] {
        background-color: #365069;
        color: white;
        }
        footer {
        background-color: #365069;
        color: white;
        }
        a[href="https://streamlit.io/cloud"] {
        display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    main_app.run()

except Exception as e:
    st.error("Haribol!! Got some error")
    st.write(e)

    if main_app.in_development:
        st.write(e)
    if main_app.userinfo:
        if 'dev' in main_app.userinfo['roles']:
            st.write(e)

# st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")