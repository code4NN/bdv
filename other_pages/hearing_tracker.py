import streamlit as st
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
# ============= some variables end


## ----------- call back functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage

# --------------- 
def sp():
    st.header(":green[Shrila Prabhupada Vaani]")
    lecture_option = st.radio("Please choose one",options=['SB Lectures','Morning Walks'],horizontal=True)

    if lecture_option=='SB Lectures':
        # if 'spdb_sbclass' not in st.session_state.shravanam_db:
        if True:
            database = pd.read_excel("./Hearing Tracker.xlsx",sheet_name='SP_SB',skiprows=1)
            database['date_obj'] = pd.to_datetime(database['date'],format="%Y-%m-%d",errors='coerce')
            database['date_show'] = database.date_obj.apply(lambda x: x.strftime("%y %b %d"))
            st.session_state.shravanam_db['spdb_sbclass'] = database[['canto','chapter','text','Place','date_obj','date_show','final title','heard_by','URL']]

        database = st.session_state.shravanam_db['spdb_sbclass']
        st.dataframe(database)

    return
    # get the database
    if 'sp_sb_db' not in st.session_state.shravanam_db:
        st.session_state.shravanam_db['sp_sb_db'] = pd.DataFrame(
            [
            ["Hyderabad",	"1974-04-24",	"Untitled"	],
            ["Tirupati",	"1974-04-26",	"Untitled"	],
            ["Los_Angeles",	"1974-01-13",	"Untitled"	],
            ["Caracas",	"1975-02-20",	"Increasing_Your_Problems"	],
            ["Caracas",	"1975-02-21",	"The_Caracas_Is_Ford-But_Ford_Is--etc"]],
            columns=["Place",	"date final title",	"heard_by"])

    database = st.session_state.shravanam_db['sp_sb_db']
    database['dateobj'] = pd.to_datetime(database['date final title'],format="%Y-%m-%d")
    database['date_display'] = database.dateobj.apply(lambda x: x.strftime("%y-%b-%d"))
    st.dataframe(database)

    place_filter_df = database.Place.value_counts().to_frame().reset_index().rename(columns={"index":"Location",
                                                                              'Place':"Count"})
    
    # Location filter
    grid_builder = GridOptionsBuilder.from_dataframe(place_filter_df)
    grid_builder.configure_selection('multiple', use_checkbox=True,
                                        header_checkbox=True
                                        )
    grid_options = grid_builder.build()
    grid_result = AgGrid(place_filter_df,gridOptions=grid_options,fit_columns_on_grid_load=True)


    st.dataframe(place_filter_df)
    include_date_in_title = st.checkbox("Date",key='include_date_checkbox')
    include_place_in_title = st.checkbox("Place",key='include_place_checkbox')
    for i,row in database.iterrows():
        title = row['heard_by']
        if include_place_in_title:
            title = f"""{row['Place']}{'-'*5} {title}"""
        if include_date_in_title:
            title = f"""{row['date_display']}{'-'*2} {title}"""

        st.button(f":green[{title.replace('_',' ')}]",key=i)

# --------------- Wrapper
pagestate_map = {'default'}

def hearing_tracker_root():
    if 'shravanam_db' not in st.session_state:
        st.session_state['shravanam_db'] = {}

    if 'substate' not in st.session_state:
        # default behaviour
        sp()

    elif st.session_state['substate'] in pagestate_map.keys():
        # directed behaviour
        pagestate_map[st.session_state['substate']]()
    else:
        # exceptional
        pass 