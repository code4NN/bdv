import streamlit as st

# Import various classes
from other_pages.loginpage import login_Class
from other_pages.feed import feed_Class
from other_pages.settlement import settlement_Class
from other_pages.finder import finder_Class



class myapp:    
    def __init__(self,in_development,page_in_development):

        # Global parameters
        self.in_development = in_development
        self.page_in_development = page_in_development

        self.page_config = {'page_title': "BDV",
                            'page_icon':'☔',
                            'layout':'centered'
                            }
               
        # register all the page
        self.page_map = {'login':login_Class(),
                         'feed':feed_Class(),
                         'settlement':settlement_Class(),
                         'finder': finder_Class(),
                          }
        self.current_page = 'login'
        
        # User related data
        # Get's populated after login
        self.userinfo = None
        # Set the Initial Page Configuration
        # st.markdown( """
        #         <style>
        #         # #MainMenu {visibility: hidden;}
        #         # footer {visibility: hidden;}
        #         </style>
        #         """, unsafe_allow_html=True)
    
    def run(self):
        # if self.in_development:
        #     self.page_map.pop(self.page_in_development)
        #     # from other_pages.finder import finder_Class
        #     self.page_map[self.page_in_development] = finder_Class()
        #     if self.userinfo:
        #         self.current_page = self.page_in_development
        #     else :
        #         pass
        self.page_map[self.current_page].run()
# End of My App Class

# Create an instance of the voice-app
if 'bdv_app' not in st.session_state:
    st.session_state['bdv_app'] = myapp(in_development=True if st.secrets['developer']['in_development']=='1' else False,
                                        page_in_development='finder'
                                        )





# For development
main_app = st.session_state['bdv_app']
if main_app.in_development:
    PAGE_DEVELOPING = 'finder'
    PAGE_CLASS = finder_Class
    main_app.page_map[PAGE_DEVELOPING] = PAGE_CLASS()



st.set_page_config(**main_app.page_config)





try:
    main_app.run()

except Exception as e:
    st.error("Haribol!! Got some error")

    if main_app.in_development:
        st.write(e)

# st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")












