import streamlit as st
import datetime

class page4_feed:
    def __init__(self):
        
        self.subpage = 'home'
        self.subpage_navigator = {
            'home':self.home
        }
    def go2page(self,page_address):
        """
        """
        st.session_state._page = page_address

    def home(self):
        # st.header(":green[Barasana Dhaam VOICE]")
        # st.image("https://rukminim1.flixcart.com/image/850/1000/jm81zm80/poster/j/j/b/medium-posri-sri-radha-gopinath-close-up-03-posri-sri-radha-original-imaf2gg6sttcgq5d.jpeg?q=90")

        st.markdown("---")
        left,middle,right = st.columns(3)
        left.button("Settlement 💸",on_click=self.go2page,args=['feed'])
    
    def run(self):
        self.subpage_navigator[self.subpage]()