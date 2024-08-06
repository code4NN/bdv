import streamlit as st

class feed_Class:
    def __init__(self):
        
        self.page_config = {'page_title': "Login Page",
                            'page_icon':'☔',
                            'layout':'wide'}
        self.page_map = {
            'home':self.home
        }
        self.current_page = 'home'
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)

    def home(self):
        st.header(":green[Barasana Dhaam VOICE]")
        st.image("https://rukminim1.flixcart.com/image/850/1000/jm81zm80/poster/j/j/b/medium-posri-sri-radha-gopinath-close-up-03-posri-sri-radha-original-imaf2gg6sttcgq5d.jpeg?q=90")

        st.markdown("---")
        
        st.subheader(":green[Quick Actions]")
        def go2page(page_name):
            self.bdvapp.current_page = page_name
        
        left,middle,right = st.columns(3)
        left.button("Settlement 💸",on_click=go2page,args=['settlement'])

        middle.button("Hearing 💊",on_click=go2page,args=['sp_hearing'])

        right.button("Class revisions",on_click=go2page,args=['revision'])
    
    def run(self):
        self.page_map[self.current_page]()