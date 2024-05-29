import os
import streamlit as st
import requests
import urllib.parse as urlparser
from bs4 import BeautifulSoup as soup
from streamlit.components.v1 import html as HTML
import pandas as pd
#%%
import pytube 
#%%
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
        self._search_results = {}
    def other(self):
        omode = st.radio("Option",['web','yt'],horizontal=True)
        if omode == 'web':
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
    
        elif omode=='yt':
            _search,watch = st.tabs(['Search','watch'])
            with _search:
                query_text = st.text_input("Enter")
                def fetch_search_results(query):
                    search = pytube.Search(query)
                    results = search.results
                    self._search_results = {v.title:v.watch_url for v in results}
                st.button("Go",on_click=fetch_search_results,args=[query_text])
                def download_video(url,filename):
                    vid = pytube.YouTube(url).streams.get_highest_resolution()
                    vid.download("./data",filename)
                    
                if len(self._search_results) > 0:
                    for t,u in self._search_results.items():
                        st.markdown(f"[{t}]({u})")
                        st.button("Download",on_click=download_video,
                                  args=[u,f"{len(os.listdir('./data'))}.mp4"],key="download_"+t)
            with watch:
                def clearall():
                    for files in os.listdir("./data"):
                        os.unlink(f"./data{files}")
                st.button("Clear all",on_click=clearall)
                available_vide = os.listdir("./data")
                for v in available_vide:
                    if st.checkbox("Show "+v):
                        st.video(f"./data/{v}",format='video/mp4')
                    
            

    def run(self):
        self.page_dict[self.current_page]()