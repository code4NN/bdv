import random
import streamlit as st
import pandas as pd
import json
import datetime

# from other_pages.googleapi import download_data
# from other_pages.googleapi import upload_data
from streamlit.components.v1 import html as display_html

class hearing_Class:
    def __init__(self):
        
        self.page_config = {'page_title': "Shravanam",
                            'page_icon':'💊',
                            'layout':'wide'}
        self.page_map = {
            'SP':self.sp_lectures,
            'Vani':self.vaani_syllabus,
            'HHRNSM':self.HHRNSM_vaani
            }
        self.current_page = 'SP'
        
        # ===================================databases=================================
        # for Prabhupada lectures------------------------------------------------------
        self.sp_sindhu_df = pd.read_csv("./local_data/SP_sindhu_config.csv")
        # user data (this is used if logged in)
        self._sp_userdb = None
        self._sp_userdb_refresh = True
        
        # prabhupada hearing page db
        self._sp_single_choice_dfdict = {'SB_canto':None,
                                     'SB_chapter':None,
                                     'SB_location':None,
                                     
                                     'update_post_date':True,
                                     'update_post_canto':True,
                                     'update_post_chapter':True,
                                     
                                     'BG_chapter':None,
                                     'BG_location':None
                                     }
        self.update_sp_sindhu_finder("category == 'SB'",['canto','chapter','location'])
        
    
    def get_sp_sindhu_value_count(self,query,column_name,new_name):
        df = self.sp_sindhu_df.copy(deep=True)
        dfsummary = df.query(query)[column_name]\
        .value_counts().reset_index().sort_values(column_name,ascending=True)
        dfsummary.columns = [new_name,'count']
        dfsummary.insert(0,'select',False)
        return dfsummary.copy()
    
    def update_sp_sindhu_finder(self,query,update_list):
        """
        * canto
        * chapter
        * location
        """
        
        if 'canto' in update_list:
            self._sp_single_choice_dfdict['SB_canto'] = self.get_sp_sindhu_value_count(query,'sb_canto','canto')
        
        if 'chapter' in update_list:
            self._sp_single_choice_dfdict['SB_chapter'] = self.get_sp_sindhu_value_count(query,'sb_ch','chapter')
            
        if 'location' in update_list:
            self._sp_single_choice_dfdict['SB_location'] = self.get_sp_sindhu_value_count(query,'location','location')
            
            
            
    @property
    def bdvapp(self):
        return st.session_state['bdv_app']
    
    def __single_select_chb_sp(self,editor_key,original_key,checkbox_column):
        """
        * editor_key = key for the st.data_editor
        * original_key = the df should be stored in st.session_state[original_key]
        * checkbox_column = name of the checkbox column
        * It must be the first column"""
        edited_rows = st.session_state[editor_key]['edited_rows']
        if len(edited_rows)==1:
            row_num = list(edited_rows.keys())[0]
            # df = st.session_state[original_key].copy(deep=True)
            df = self._sp_single_choice_dfdict[original_key].copy()
            
            set_2_True = list(edited_rows.values())[0][checkbox_column]        
            if set_2_True:
                df[checkbox_column] = False
                df.iloc[row_num,0] = True
                self._sp_single_choice_dfdict[original_key]= df.copy()
            else:
                df[checkbox_column] = False
                self._sp_single_choice_dfdict[original_key]= df.copy()
                st.session_state[editor_key]['edited_rows'] = {}
        
        if editor_key == 'sb_canto_selector':
            self._sp_single_choice_dfdict['update_post_canto'] = True
        
        elif editor_key == 'sb_chapter_selector':
            self._sp_single_choice_dfdict['update_post_chapter'] = True        
        
    def sp_lectures(self):
        st.header(":rainbow[Srila Prabhupada Ki Jai!!]")
        
        spdf = self.sp_sindhu_df # load the lecture config file
        st.dataframe(spdf)
        subsubpage_dict = {1:'SB',
                           2:'BG',
                           3:'MW, RC etc',
                           4:'Locate a Lecture'}
        
        section_index = st.radio("Choose a Section",
                              options=range(1,len(subsubpage_dict.keys())+1),
                              index=0,
                              format_func=lambda x: subsubpage_dict[x],
                              horizontal=True
                              )
        if section_index == 1:
            # SB corner
            # 1. first display as many tabs as bookmarks in the file (if logged in)
            # 2. Show a search-box for searching lectures plus a display of results
            # 3. selector
            #     -> Date (year, month and day)
            #     -> Canto
            #     -> Chapter
            #     -> Location
            #    -> results in data frame
            date_filter = []
            def checkbox_handler():
                if not st.session_state['date_filter_checkbox']:
                    self.update_sp_sindhu_finder("category == 'SB'",
                                                 ['canto','chapter','location'])
            if st.checkbox("Add date filter",key='date_filter_checkbox',on_change=checkbox_handler):
                def sp_date_handler():
                    self._sp_single_choice_dfdict['update_post_date'] = True
                chosen_date = st.date_input("Enter date", 
                                            format="YYYY-MM-DD",
                                            min_value=datetime.date(1966,2,19), # hardcoded from excel
                                            max_value=datetime.date(1977,7,1), # hardcoded from excel
                                            value=datetime.date(1972,
                                                                datetime.datetime.today().month,
                                                                datetime.datetime.today().day),
                                            on_change=sp_date_handler)
                chosen_year = chosen_date.year
                chosen_month = chosen_date.month
                chosen_day = chosen_date.day
                
                date_filter = ["category == 'SB' ",f"year == {chosen_year}", f"month == {chosen_month}"]
                if not st.toggle("Ignore day", value=True,on_change=sp_date_handler):
                    date_filter.append(f"day == {chosen_day}")
                
                spdf = spdf.query(" and ".join(date_filter))
                if self._sp_single_choice_dfdict['update_post_date']:
                    self.update_sp_sindhu_finder(' and '.join(date_filter),
                                                 ['canto','chapter','location'])
                    self._sp_single_choice_dfdict['update_post_date'] = False
                st.caption(f"found {len(spdf)} records from 1849")
                
                
            # further filters of canto- chapter location
            st.divider()
            left,middle,right = st.columns(3)
            with left:
                st.markdown("Choose Canto")                
                list_chosen_canto = st.data_editor(self._sp_single_choice_dfdict['SB_canto'],
                                                   hide_index=True,
                                                   column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                                  'canto':st.column_config.NumberColumn('Canto')},
                                                   key='sb_canto_selector',
                                                   on_change=self.__single_select_chb_sp,
                                                   args=['sb_canto_selector','SB_canto','select']
                                                   ).query("select == True")['canto'].tolist()
                
                if list_chosen_canto :
                    cantoquery = f"sb_canto == {list_chosen_canto[0]}"
                    spdf = spdf.query(cantoquery)
                    
                # update only when canto is changed
                if self._sp_single_choice_dfdict['update_post_canto']:
                    querylist = ["category == 'SB'",*date_filter]
                    if list_chosen_canto:
                        querylist.append(cantoquery)
                    self.update_sp_sindhu_finder(' and '.join(querylist),
                                                ['chapter','location'])
                    self._sp_single_choice_dfdict['update_post_canto'] = False
                    
                st.caption(len(spdf))
            
            with middle:
                st.markdown("Choose Chapter")
                list_chosen_chapter = st.data_editor(self._sp_single_choice_dfdict['SB_chapter'],
                                                   hide_index=True,
                                                   column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                                  'chapter':st.column_config.NumberColumn('Chapter')},
                                                   key='sb_chapter_selector',
                                                   on_change=self.__single_select_chb_sp,
                                                   args=['sb_chapter_selector','SB_chapter','select']
                                                   ).query("select == True")['chapter'].tolist()
                if list_chosen_chapter:
                    chapterquery = f" sb_ch == {list_chosen_chapter[0]}"
                    spdf = spdf.query(chapterquery)
                
                # update only if chapter edited
                if self._sp_single_choice_dfdict['update_post_chapter']:
                    querylist = ["category == 'SB' ",*date_filter]
                    if list_chosen_canto:
                        querylist.append(cantoquery)
                    if list_chosen_chapter:
                        querylist.append(chapterquery)
                    chapterquery = "" if not list_chosen_canto else f"{chapterquery}"
                    self.update_sp_sindhu_finder(' and '.join(querylist),
                                                 update_list=['location'])
                    self._sp_single_choice_dfdict['update_post_chapter'] = False
                    
            
            with right:
                st.markdown("Choose Location")
                list_chosen_location = st.data_editor(self._sp_single_choice_dfdict['SB_location'],
                                                   hide_index=True,
                                                   column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                                  'location':st.column_config.NumberColumn('Location')},
                                                   key='sb_location_selector',
                                                   on_change=self.__single_select_chb_sp,
                                                   args=['sb_location_selector','SB_location','select']
                                                   ).query("select == True")['location'].tolist()
                if list_chosen_location:
                    spdf = spdf.query(f"location == {list_chosen_location[0]}")
            
            # now we have all the filters applied. Just display the filtered
            st.divider()
                    

        elif section_index == 2:
            # BG corner
            # 1. first display as many tabs as bookmarks in the file (if logged in)
            # 2. Show a search-box for searching lectures plus a display of results
            # 3. selector
            #     -> Chapter
            #     -> Location
            #     -> Date (popover year, month and day)
            #    -> results
            pass
        
        elif section_index == 3:
            # All other
            # Level 2 filter
            # Choose among the other series
            sub_section_dict = {1:'Morning Walks',
                                2:'Room Conversations',
                                3:'Interviews',
                                4:'Public Lectures',
                                5:'Festival'
                                # some more
                                }
            sub_section_index = st.radio("Choose a Sub-Section",
                              options=range(1, len(sub_section_dict.keys())+1),
                              index=0,
                              format_func=lambda x: sub_section_dict[x],
                              horizontal=True
                              )
            if sub_section_index == 1:
                # follow this template for all...
                # 0. heading for Morning Walks
                # 1. first display as many tabs as bookmarks in the file (if logged in)
                
                # 2. display a table with filters of (location, year)
                pass
        
        elif section_index == 4:
            # Locate a lecture
            # 1. Show a search-box for searching lectures plus a display of results
            # 2. keep following filters in order
            #       > Date
            #       > Section (SB, BG etc) (also canto chapter for SB and BG )
            #       > Locationx
            pass


    def vaani_syllabus(self):
        pass
    
    def HHRNSM_vaani(self):
        pass

    def run(self):
        st.markdown(
        """
        <style>
        .step-up,
        .step-down {
            display: none;
        }
        </style>
        </style>
        """,
        unsafe_allow_html=True
        )
        # display the available series in the sidebar
        # Until one have completed Vaani syllabus
        # Show vaani syllabus
        # else show the other view
        # with st.sidebar:
        #     with st.expander("DD Series"):
        #         pass
        
        # with st.sidebar:
        #     with st.expander("Srila Prabhupada",expanded=True):
        #         st.button("SB Lectures",on_click=self.change_page,args=['SP_SB'],
        #                   type='primary' if self.current_page=='SP_SB' else 'secondary')
                
        #         st.button("Morning Walks",on_click=self.change_page,args=['SP_MW'],
        #                   type='primary' if self.current_page=='SP_MW' else 'secondary')

        #         st.button("Bhagwad Gita",on_click=self.change_page,args=['SP_BG'],
        #                   type='primary' if self.current_page=='SP_BG' else 'secondary')
        
        # have a varible which is activated while playing a lecture
        # and deactivated when pressed back button
        self.page_map.get(self.current_page,'SP')()
# --------------- 

# if 'app' not in st.session_state:
#     st.session_state.app = hearing_Class()

# st.session_state['app'].run()