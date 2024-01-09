import streamlit as st
import requests
import urllib.parse as urlparser
from bs4 import BeautifulSoup as soup
from streamlit.components.v1 import html as display_html
import pandas as pd

class finder_Class:
    def __init__(self):
        
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
    
    
    # @property
    # def bdvapp(self):
    #     return st.session_state.get('bdv_app',None)
    
    # def home(self):
    #     pass
    # def vedabase_SP(self):
    #     pass
    # def developer_page(self):
    #     ROOT = "https://vedabase.io/en/library/transcripts/?type=Srimad-Bhagavatam"
        
    #     use_default = st.checkbox("use default")
    #     URL_tofetch = st.text_input("put URL",value=ROOT if use_default else "")
        
    #     response = self.fetch_URL(URL_tofetch)
    #     document = soup(response.text,"html.parser")        
    #     type_filters= []
    #     year_filter = []
    #     location_filters = []
    #     # fill with following dicts
    #     # {title:
    #     # dataframe:}
    #     last_seen_title = "Filter by type"
    #     # Iterate over all the filters
    #     for filterblock in document.find(id='facets').find_all(class_='facet-block'):
    #         filter_title = filterblock.find("h3").text.strip()
    #         if filter_title in ['Filter by year','Filter by location']:
    #             last_seen_title = filter_title

    #         item_list = []
    #         # Fill the list in order of 
    #         # [value, count, is_active]
    #         # Iterate over all the options available
    #         for one_option in filterblock.find_all("li"):
    #             # value and count
    #             available_count = one_option.find("span").text.strip()
    #             value_name = one_option.find("a").text.strip().replace(available_count,"").strip()
    #             available_count = int(available_count.replace("(","").replace(")","").replace(" ",""))
    #             # is active
    #             is_active = False
    #             if one_option.has_attr("class"):
    #                 if 'active' in one_option['class']:
    #                     is_active= True
    #             # Query
    #             # query = one_option.fin("a").get("href")
    #             # now create the list
    #             item_list.append([value_name,available_count,is_active])
    #         if item_list:
    #             dataframe = pd.DataFrame(item_list,
    #                                      columns=['options','count','is_active'])
    #         else :
    #             dataframe = -1
    #         filter_information = {'title':filter_title.replace("Filter by ",""),
    #                               'dataframe':dataframe}
    #         # now add based on last seen title
    #         if last_seen_title == 'Filter by type':
    #             type_filters.append(filter_information)
    #         elif last_seen_title == 'Filter by year':
    #             year_filter.append(filter_information)
    #         elif last_seen_title == 'Filter by location':
    #             location_filters.append(filter_information)
    #         else :
    #             st.error("something went wrong")
        
    #     left,middle,right = st.columns(3)
    #     def filter_displayer(container,filter_dictionary):
    #         response_queries = []
    #         with container:
    #             for a_filter in filter_dictionary:
    #                 st.subheader(a_filter['title'])
    #                 response = st.data_editor(a_filter['dataframe'],
    #                                 disabled=['_index','options','count',],
    #                                 hide_index=True,
    #                                 column_config={
    #                                     "options":st.column_config.Column("Choices",
    #                                                             ),
    #                                     "count":st.column_config.NumberColumn("count",
    #                                                                         format="%d"),
    #                                     "is_active":st.column_config.CheckboxColumn("Select",
    #                                                                                 )
    #                                 }
    #                 )
    #                 response = response.query(" is_active == True ")
    #                 for _,row in response.iterrows():
    #                     response_queries.append(f"{a_filter['title']}={row['options']}")
    #         return response_queries
        
    #     query1 = filter_displayer(left,type_filters)
    #     query2 = filter_displayer(middle,year_filter)
    #     query3 = filter_displayer(right,location_filters)
    #     query_list = [*query1,*query2,*query3]
    #     if query_list:
    #         newURL = "https://vedabase.io/en/library/transcripts/?"+"&".join(query_list).replace(" ","+")
    #         response = requests.get(newURL)
    #         display_html(response.text,height=500,scrolling=True)

    # def idt_lectures_by_HHRNSM(self):
    #     pass
    

    def run(self):
        self.page_dict[self.current_page]()