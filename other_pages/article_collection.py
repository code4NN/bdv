import streamlit as st
import json
import pandas as pd

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
COLLECTION_RANGE = 'article_collection!A:E'
# ============= some variables end


## ----------- call back functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage

## -------------

def home():
    if 'database' not in st.session_state.article_collection:
        array = download_data(db_id=1,range_name=COLLECTION_RANGE)
        df = pd.DataFrame(array[1:],columns=array[0])
        
        st.session_state['article_collection']['database'] = df

    database = st.session_state.article_collection['database']
    st.header(":green[Get the right article]")
    st.dataframe(database)
# ---------------------- Wrapper
pagestate_map = {
    'default':home
}

def get_article_main():
    if 'article_collection' not in st.session_state:
        st.session_state['article_collection'] = {}

    if 'substate' not in st.session_state:
        # default behaviour
        home()

    elif st.session_state['substate'] in pagestate_map.keys():
        # directed behaviour
        pagestate_map[st.session_state['substate']]()
    else:
        # exceptional
        pass 