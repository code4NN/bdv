import streamlit as st
import pandas as pd
import json
import datetime

# from other_pages.googleapi import download_data
# from other_pages.googleapi import upload_data
from streamlit.components.v1 import html as display_html

class hearing_Class:
    def __init__(self) -> None:
        
        self.page_config = {'page_title': "Shravanam",
                            'page_icon':'💊',
                            'layout':'centered'}
        self.page_map = {
            'SP':self.sp_lectures,
            }
        self.current_page = 'SP'
        
        # databases
        # for Prabhupada SB lectures
        self._spsb_db_range = None
        self._spsb_db = None
        self._spsb_db_refresh = True                
            
    @property
    def bdvapp(self):
        return st.session_state['bdv_app']


    def sp_lectures(self):
        st.header(":rainbow[Srila Prabhupada Ki Jai!!]")
        
        
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
            #     -> Canto
            #     -> Chapter
            #     -> Location
            #     -> Date (popover year, month and day)
            #    -> results
            pass
            url = st.text_input("Enter url")
            # Define the URL you want to embed

            # HTML code for the iframe with scrollable and styled border
            html_code = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <style>
                    .iframe-container {{
                        position: relative;
                        overflow: auto;
                        padding-top: 56.25%; /* 16:9 Aspect Ratio */
                    }}
                    .iframe-container iframe {{
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        border: 5px solid gray; /* Thick gray border */
                        border-radius: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="iframe-container">
                    <iframe src="{url}" frameborder="0" allowfullscreen></iframe>
                </div>
            </body>
            </html>
            """

            # Embed the HTML in Streamlit
            display_html(html_code, height=500)

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
        # Until one have completed Vaani syllabus
        # Show vaani syllabus
        # else show the other view
        with st.sidebar:
            with st.expander("DD Series"):
                pass
        
        with st.sidebar:
            with st.expander("Srila Prabhupada",expanded=True):
                st.button("SB Lectures",on_click=self.change_page,args=['SP_SB'],
                          type='primary' if self.current_page=='SP_SB' else 'secondary')
                
                st.button("Morning Walks",on_click=self.change_page,args=['SP_MW'],
                          type='primary' if self.current_page=='SP_MW' else 'secondary')

                st.button("Bhagwad Gita",on_click=self.change_page,args=['SP_BG'],
                          type='primary' if self.current_page=='SP_BG' else 'secondary')
        
        # have a varible which is activated while playing a lecture
        # and deactivated when pressed back button
        self.page_map.get(self.current_page,'SP_SB')()
# --------------- 

if 'app' not in st.session_state:
    st.session_state.app = hearing_Class()

st.session_state['app'].run()