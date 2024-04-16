import streamlit as st

import pandas as pd
import json

import requests
from streamlit.components.v1 import html as display_pdf

from other_pages.googleapi import download_data,upload_data

class sskkb:
    def __init__(self):
        self.page_config = {'page_title': "Articles Tagging",
                    'page_icon':'🔎',
                    'layout':'wide'}
        self.page_dict = {
            'search':self.search,
            'tagging':self.tagme,
        }
        self.current_page = 'tagging'
        
        self._database_range = 'SKKB!A:F'
        self._database_refresh = True
        self._database = None
        
        self.active_magazine = None
        self.have_active_magazine = False
        
        self._n_article = 1
    
    @st.cache
    def getcontent(self,url):
        try:
            response = requests.get(url)
            # Check if response status code is in the 2xx range for successful requests
            if response.status_code // 100 == 2:
                return (1,response.text)
            else:
                # print(f"Error: {response.status_code}")
                return (0,-1)
        except requests.RequestException as e:
            # print(f"An error occurred: {e}")
            return (0,-1)
        
    
    @property
    def database(self):
        if self._database_refresh:
            # download a fresh copy
            array = download_data(3,self._database_range)
            df = pd.DataFrame(array[1:],columns=array[0])
            df['status'] = df['status'].astype('int')
            df['ID'] = df['ID'].astype('int')
            df['# A'] = df['articles'].apply(lambda x : 0 if x == '' else len(json.loads(x)))
            
            self._database = df.copy()
            self._database_refresh = False
        return self._database
    
    def tagme(self):
        mydataframe = self.database
        article_count = mydataframe['# A'].sum()
        magazine_count = mydataframe['status'].sum()
        st.header(f":gray[Total Articles:] :violet[{article_count}]")
        st.header(f":gray[Total Magazines completed:] :violet[{magazine_count}]")
        
        st.dataframe(mydataframe[['ID','# A','status']].style.highlight_max(subset=['status'],color='green'),hide_index=True)
        selectedid = st.number_input(":gray[Enter ID]",step=1,min_value=0,max_value=mydataframe.ID.max(),
                                     value=mydataframe.query("status == 0")['ID'].tolist()[0])
        # if selectedid:
        df = mydataframe.query(f"ID == {selectedid}")
        def loadthis(article_df):
            self.active_magazine = article_df.iloc[0].to_dict()
            self.have_active_magazine = True
            
        st.button('Load this',on_click=loadthis,args=[df])    
        
        if not self.have_active_magazine:
            st.warning("Please select a magazine first!!")
        else:
            st.divider()
            st.markdown(f"[Open This]({self.active_magazine['URL']})")
            st.markdown(f"### :rainbow[{self.active_magazine['issue']} - {':green[Done]' if self.active_magazine['status'] == 1 else ':red[To Do]'}]")
            
            articles = []
            global_valid = 1
            not_empty = self.active_magazine['articles'] != '' # True means we have some data filled
            pre_filled_dict = []
            if not_empty:
                pre_filled_dict = json.loads(self.active_magazine['articles'])
                if self._n_article > len(pre_filled_dict):
                    pass
                else:
                    self._n_article = len(pre_filled_dict)
            # st.write(pre_filled_dict)
            # this is the loop
            for i in range(self._n_article):
                st.markdown(f"#### :gray[Article Number:] :violet[{i+1}]")
                # i < len(pre_filled_dict)
                default_dict = pre_filled_dict[i] if not_empty and i < len(pre_filled_dict) else {'title':'',
                                                                        'titled':'',
                                                                        'author':'SGGSM',
                                                                        'source':'',
                                                                        'size':'snippet'}
                valid = 1
                
                yourheading = st.text_input(":gray[your heading]",key=f"_{i}_your_heading",
                                            value=default_dict['titled'])
                article_heading = st.text_input(":orange[article heading]",key=f"_{i}_article_heading",value=default_dict['title'])
                if not article_heading:
                    valid *=0
                
                author_list = ['SGGSM', 'SP','BSST']
                if default_dict['author'] not in author_list:
                    author_radio = len(author_list)
                else:
                    author_radio = author_list.index(default_dict['author'])
                author = st.radio(":orange[author]",options=[*author_list,'other'],key=f"_{i}_article_author_radio",horizontal=True,
                                    index=author_radio)
                if author == 'other':
                    author = st.text_input(":orange[author]",key=f"_{i}_article_author",
                                            value=default_dict['author'])
                    if not author:
                        valid *=0
                
                reference = st.text_input(":gray[source]",key=f"_{i}_article_source",value=default_dict['source'])
                if not reference:
                    reference = '-'
                size_list = ['snippet','article','theme']
                articlesize = st.radio(":orange[size]",options=['snippet','article','theme'],format_func=lambda x: {'snippet':'snippet (1-2 paragraph)',
                                                                'article':'article (max 1 page)',
                                                                'theme':'thematic (over 1 page)'}[x],
                                        key=f"_{i}_article_size",
                                        horizontal=True,
                                        index=size_list.index(default_dict['size']))
                
                articles.append({'title':article_heading,
                                    'titled':yourheading,
                                    'author':author,
                                    'source':reference,
                                    'size':articlesize})
                global_valid *=valid
                st.divider()
            def add_one(i):
                if i == 1:
                    self._n_article += 1
                elif self._n_article > 1:
                    self._n_article -=1
            
            mark_done = st.checkbox("Mark as completed",key='mark_completed_')
            mark_done = 1 if mark_done else 0
            
            left,middle,right  = st.columns(3)
            left.button("add more entries",on_click=add_one,args=[1])
            right.button("drop last entri",add_one,args=[-1],disabled= self._n_article ==1)
            
            
            with middle:
                if global_valid!=0:
                    def push_to_sheet(article,_mark_done,magazine):
                        _r = magazine['row_number']
                        article_dump = json.dumps(articles)
                        update_content = [[article_dump,_mark_done]]
                        upload_data(3,f"SKKB!E{_r}:F{_r}",update_content)
                        # clean up
                        self._n_article = 1
                        st.session_state['mark_completed_'] = False
                        # st.session_state['_0_your_heading']  = ''
                        # st.session_state['_0_article_heading'] = ''
                        # st.session_state['_0_article_author'] = ''
                        # st.session_state['_0_article_source'] = ''
                        
                        self._database_refresh = True
                        db = self.database
                        db2 = db.query("status == 0")
                        
                        self.active_magazine = db2.iloc[0].to_dict()
                        self.have_active_magazine = True
                                                
                    st.button("Submit 🚀",on_click=push_to_sheet,args=[articles,mark_done,self.active_magazine])
                else:
                    st.button("Submit 🚀",disabled=True)
                
                
    def search(self):
        pass
    
    def run(self):
        self.page_dict[self.current_page]()

# if 'instance' not in st.session_state:
#     st.session_state['instance'] = sskkb()
# app = st.session_state['instance']
# app.run()