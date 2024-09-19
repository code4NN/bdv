import streamlit as st

from query_params_handler import process_query_parameters

# Import various classes
from other_pages.loginpage import login_Class
from other_pages.feed import feed_Class

from other_pages.hearing_tracker import SP_hearing_Class
from other_pages.hearing_tracker import VANI_hearing_class

from other_pages.lecture_notes import class_notes_Class
from other_pages.thematic_encyclopaedia import sskkb
from other_pages.song_shloka import memorize_song_shloka

class myapp:
    def __init__(self):

        # Global parameters
        self.in_development = False

        # register all the page
        self.page_map = {
            'login':login_Class(),
            'feed':feed_Class(),
            
            # hearing related projects
            'sp_hearing': SP_hearing_Class(),
            'vani_hearing':VANI_hearing_class(),
            
            'revision': class_notes_Class(),
            'article_tag':sskkb(),
            'ssong':memorize_song_shloka(),
            }
        # landing page
        self.current_page = 'login'
        
        # query parameters
        self.handled_query_params = False
        
        # User related data
        self.userinfo = None
        self.user_exists = False
    
    @property
    def page_config(self):
        return self.page_map[self.current_page].page_config

    
    def quick_login(self):
        """
        updates app.userinfo if the valid user is there
        """
        login_page = self.page_map['login']
        login_page.quick_login()
    
    def reset_userdb_creds(self):
        login_page = self.page_map['login']
        login_page._creds_db_refresh = True
        _ = login_page.userdb
        user,password = self.userinfo['full_username'],self.userinfo['password']
        login_page.perform_login(user,password,'submit')
        
    def run(self):
                                    
        # custom global css
        # if not self.in_development:
        # if False:
        if True:
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
            
        self.page_map[self.current_page].run()
        
# End of My App Class



# Create an instance of the voice-app
if 'bdv_app' not in st.session_state:
    st.session_state['bdv_app'] = myapp()

main_app = st.session_state['bdv_app']

st.set_page_config(**main_app.page_config)


try:
    if not main_app.handled_query_params:
        if st.query_params:
            process_query_parameters(main_app,st.query_params)
    # st.write(main_app.userinfo)
    # st.write(main_app.current_page)
    main_app.run()

except Exception as e:
    st.error("Haribol!! Got some error")
    st.write(e)

# st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")