import streamlit as st
import requests
from bs4 import BeautifulSoup as soup
from streamlit.components.v1 import html as display_html


class finder_Class:
    def __init__(self):
        
        self.page_dict = {'home':self.home,
                          'sp_transcript':self.vedabase_SP,
                          'idt_hhrnsm':self.idt_lectures_by_HHRNSM,
                          'developer':self.developer_page}
        self.current_page = 'developer'
    
    @st.cache_data()
    def fetch_URL(_self,URL):
        return requests.get(url=URL)
    
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)
    
    def home(self):
        pass
    def vedabase_SP(self):
        pass
    def developer_page(self):
        if st.checkbox("home"):
            self.bdvapp.current_page = 'feed'
            self.bdvapp.run()
            # st.rerun()

        # self.bdvapp.
        ROOT = "https://vedabase.io/en/library/transcripts/"
        response = self.fetch_URL(ROOT)
        with st.sidebar:
            height = st.number_input("height of window",min_value=0,value=600,step=50)
            height2 = st.number_input("window 2",min_value=100,value=600,step=100)
            height3 = st.number_input("window 3",min_value=100,value=600,step=100)
        
        display_html(response.text,height=height,scrolling=True)
        document = soup(response.text,"html.parser")
        
        for filterblock in document.find(id='facets').find_all(class_='facet-block'):
            st.write(filterblock)




        URL = st.text_input("--")
        if URL:
            response = self.fetch_URL(ROOT+URL.split("library/transcripts/")[1])
            display_html(response.text,height=height2,scrolling=True)
        
        URL = st.text_input("---")
        if URL:
            response = self.fetch_URL(ROOT+URL.split("library/transcripts/")[1])
            display_html(response.text,height=height3,scrolling=True)
        

    def idt_lectures_by_HHRNSM(self):
        pass
    

    def run(self):
        self.page_dict[self.current_page]()