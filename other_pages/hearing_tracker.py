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
                            'layout':'centered'}
        self.page_map = {
            'SP':self.sp_lectures,
            'Vani':self.vaani_syllabus,
            'HHRNSM':self.HHRNSM_vaani
            }
        self.current_page = 'SP'
        
        # ===================================databases=================================
        # for Prabhupada lectures------------------------------------------------------
        self._spsb_db = None
        self._spsb_db_refresh = True
        # user data (this is used if logged in)
        self._sp_userdb = None
        self._sp_userdb_refresh = True
        
        # prabhupada hearing page db
        self._sp_single_choice_dfdict = {'SB_canto':None,
                                     'SB_chapter':None,
                                     'SB_location':None,
                                     
                                     'BG_chapter':None,
                                     'BG_location':None
                                     }
        
            
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
            # update the self._sp_singl_choice_dfdict['chapter']
            pass
        elif editor_key == 'sb_chapter_selector':
            # update the self._sp_singl_choice_dfdict['location']
            pass
        
    def sp_lectures(self):
        st.header(":rainbow[Srila Prabhupada Ki Jai!!]")
        
        spdf = None # load the lecture config file
        
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
            
            # search box and search filter
            search_query = st.text_input("Search a lecture").strip()
            if st.checkbox("Add date filter"):
                chosen_date = st.date_input("Enter date", 
                                            format="YYYY-MM-DD",
                                            min_value=datetime.date(1966,1,1),
                                            max_value=datetime.date(1977,12,31),
                                            value=datetime.date(1970,1,1))
                
                ignore_day = st.toggle("Ignore day", value=True)

                # filter spdf usign date
                
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
                    spdf = spdf.query(f"canto == {list_chosen_canto[0]}")
            
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
                    spdf = spdf.query(f"chapter == {list_chosen_chapter[0]}")
            
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
        self.page_map.get(self.current_page,'SP_SB')()
# --------------- 

if 'app' not in st.session_state:
    st.session_state.app = hearing_Class()

st.session_state['app'].run()