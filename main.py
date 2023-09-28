import streamlit as st

# Import various pages
from other_pages.loginpage import page4_login


class myapp:
    
    def __init__(self):
        # Some Global parameters
        self.PAGE_LAYOUT = 'centered'
        self.PAGE_TITLE = 'BDV'        

        # Page navigation
        self.current_page = 'login'
        self.all_pages = {'login':page4_login,
                          }
        
        # Set the Initial Page Configuration
        st.set_page_config(page_title=self.PAGE_TITLE,
                            page_icon='☔',
                            layout=self.LAYOUT
                            )
        # st.markdown( """
        #         <style>
        #         # #MainMenu {visibility: hidden;}
        #         # footer {visibility: hidden;}
        #         </style>
        #         """, unsafe_allow_html=True)
    
    def run(self):
        self.all_pages[self.current_page].run()
# End of My App Class

if 'main_app' not in st.session_state:
    st.session_state['main_app'] = myapp()

try:
    st.session_state['main_app'].run()
except Exception as e:
    st.error("Haribol!! Got some error")

    # for deployed. send a wa message to maintainer with the error
    # for development show a checkbox to show the error
    if st.checkbox("Show the error"):
        st.write(e)

st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")












