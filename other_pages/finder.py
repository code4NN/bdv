import streamlit as st
import requests
from streamlit.components.v1 import html as HTML

class finder_Class:
    def __init__(self):
        # page map
        self.page_config = {'page_title': "Login Page",
                            'page_icon':'☔',
                            'layout':'centered'}
        self.page_dict = {
                        #     'home':self.home,
                        #   'sp_transcript':self.vedabase_SP,
                        #   'idt_hhrnsm':self.idt_lectures_by_HHRNSM,
                        #   'developer':self.developer_page,
                          'other':self.other}
        self.current_page = 'other'
    def other(self):
        tabs = st.tabs(["main",'secondary','info'])
        with tabs[2]:
            height = st.number_input("height",value=600)
        with tabs[0]:
            URL = st.text_input("URL",key='1input')
            if URL:
                URL = f"https://{URL.split('://')[2]}"

                contents = requests.get(URL).text
                HTML(contents.replace("http",'||').replace("https",'hari'),height=height,scrolling=True)

        with tabs[1]:
            URL = st.text_input("URL",key='2input')
            if URL:
                URL = f"https://{URL.split('://')[2]}"

                contents = requests.get(URL).text
                HTML(contents.replace("http",'||').replace("https",'hari'),height=height,scrolling=True)

    def run(self):
        self.page_dict[self.current_page]()