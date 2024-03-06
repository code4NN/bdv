import streamlit as st
import pandas as pd
import json
import datetime
# from st_aggrid import AgGrid, GridOptionsBuilder

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

class hearing_Class:
    def __init__(self) -> None:
        
        self.page_config = {'page_title': "Shravanam",
                            'page_icon':'💊',
                            'layout':'centered'}
        self.page_map = {
            'SP_SB':self.sp_SB_lectures,
            }
        self.current_page = 'SP_SB'
        
        # databases
        # for Prabhupada SB lectures
        self._spsb_db_range = None
        self._spsb_db = None
        self._spsb_db_refresh = True                
            
    @property
    def bdvapp(self):
        return st.session_state['bdv_app']


    def sp_SB_lectures(self):
        st.header(":rainbow[Srila Prabhupada]")
        st.title(":rainbow[SB Classes]")
        
        # Radio button for three pages
        # 1. Your Selected playlist
        # 2. SB Order as per canto, chapter text
        # 3. Locate and hear
        # 4. Lectures in progress
        subsubpage_dict = {1:'Your Playlist',
                           2:'Sorted by SB',
                           3:'Lectures in Progress'}
        subsubpage = st.radio("Choose a Section",
                              options=range(1,len(subsubpage_dict.keys())-1),
                              index=0,
                              format_func=lambda x: subsubpage_dict[x],
                              horizontal=True
                              )
        
        # now get the database for this series
        # hearing database --> hdb
        hdb = self._spsb_db
        # and various values from these
        # keep two broad division
        # hearing db, and user 
        if subsubpage == 1:
            st.subheader(":rainbow[Your Playlist]")
            # get the following functionality
            """
            Basically this is the currently active lecture which we plan to hear..
            .. maybe in a week or in a month or as per devotee's choice
            * create a new playlist
            * reset a playlist (mark all as unheard)
            * Empty the playlist
            """
            pass
        elif subsubpage==2:
            st.subheader(":rainbow[Sorted By Srimad Bhagavatam]")
            """
            * Show all canto, and how many remaining lectures
            * Show active chapter and remaining lectures
            * Show list of lectures based on active selection
            """
            pass
        elif subsubpage ==3:
            st.subheader(":rainbow[Lectures in Progress]")
            """
            Whatever lecture is marked as hearing will appear here
            """
            pass
        
        
        
    
    def change_page(self,target_page):
        """Change Page

        Args:
            target_page (page_id):
        """
        self.current_page = target_page

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
        with st.sidebar:
            with st.expander("Srila Prabhupada",expanded=True):
                st.button("SB Lectures",on_click=self.change_page,args=['SP_SB'],
                          type='primary' if self.current_page=='SP_SB' else 'secondary')
                
                st.button("Morning Walks",on_click=self.change_page,args=['SP_MW'],
                          type='primary' if self.current_page=='SP_MW' else 'secondary')

                st.button("Bhagwad Gita",on_click=self.change_page,args=['SP_BG'],
                          type='primary' if self.current_page=='SP_BG' else 'secondary')
        
        self.page_map.get(self.current_page,'SP_SB')()
# --------------- 