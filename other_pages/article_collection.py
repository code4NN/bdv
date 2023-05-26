import streamlit as st
import json
import pandas as pd

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
COLLECTION_RANGE = 'article_collection!A:E'
TAGGING_DATABASE = 'working_database!A:P'
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
    
    # st.write(st.session_state)
    if st.session_state.user['name'] =='Shivendra':
        st.button("Contribute",on_click=change_subpage,args=['tagging_activity'])

    st.dataframe(database)

    st.markdown('---')
    st.button('home',key='home',on_click=change_page,args=['feed','default'])


def tagging_activity():
    if 'edit_database' not in st.session_state.article_collection:
        dataarray = download_data(db_id=3,range_name=TAGGING_DATABASE)
        dataframe = pd.DataFrame(dataarray[1:],columns=dataarray[0])

        st.session_state.article_collection['edit_database'] = dataframe

    
    st.header(":green[Welcome to the Article Tagging zone]")
    database = st.session_state.article_collection['edit_database']
    
    st.dataframe(database.head())
# ---------------------- Wrapper
pagestate_map = {
    'default':home,
    'tagging_activity':tagging_activity
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