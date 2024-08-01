import streamlit as st
from query_params_handler import process_query_parameters


# Import various classes
# available for all devotees
from other_pages.loginpage import login_Class
from other_pages.sadhana_card import sadhana_card_class
from other_pages.settlement import settlement_Class
from other_pages.accounts import account_Class
from other_pages.hearing_tracker import hearing_Class

# for personal usages
from other_pages.thematic_encyclopaedia import sskkb
from other_pages.song_shloka import memorize_song_shloka
from other_pages.lecture_notes import class_notes_Class

class myapp:
    def __init__(self):

        # Global parameters
        self.in_development = False

        # register all the page
        self.page_map = {
            # public
            'login':login_Class(),
            'sadhana_card':sadhana_card_class(),
            'settlement':settlement_Class(),
            'dpt_accounts': account_Class(),
            'heart_medicine': hearing_Class(),
            
            # private
            'revision': class_notes_Class(),
            'article_tag':sskkb(),
            'ssong':memorize_song_shloka(),
            }
        
        # landing page
        self.current_page = 'login'
        
        # query parameter handling flag
        self.handled_query_params = False
        
        # User related data
        self.userinfo = None
    
    @property
    def page_config(self):
        return self.page_map[self.current_page].page_config

    def run(self):
                                    
        # custom global css
        if st.secrets['developer']['add_topheaderCSS']=='yes':
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
        process_query_parameters(main_app,st.query_params) 
    main_app.run()

except Exception as e:
    st.error("Haribol!! Got some error")
    st.write(e)