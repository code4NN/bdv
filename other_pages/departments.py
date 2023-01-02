import streamlit as st
import pandas as pd
import json
import time
from other_pages.googleapi import fetch_data
from other_pages.googleapi import update_range

from other_pages.googleapi import append_range

def change_subpage(subpage):
    st.session_state['substate'] = subpage
def change_page(page):
    st.session_state['state'] = page

# ---------------------- some constants
sheetID = st.secrets['credentials']['sheetID']
# ---------------------- Functions
def show_departments():
    st.subheader("VOICE Structure")
    
    df_raw = fetch_data(sheetID,'departments!A1:F57')
    df = pd.DataFrame(df_raw[1:],columns=df_raw[0])

    parent_depts = sorted(df.loc[:,'parent department'].unique().tolist())
    
    st.button('Show by devotee',on_click=change_subpage,args=['showbydev'])
    st.button('Feed',on_click=change_page,args=['feed'])

    dept = st.radio(":blue[select department]",options=['all',*parent_depts],
                    label_visibility='hidden')
    
    st.markdown("---")
    st.markdown(f'## :blue[{dept}]')

    subdepts = None
    if dept =='all':
        subdepts = df
    else :
        subdepts = df[df['parent department'] == dept].reset_index()
    
    st.dataframe(subdepts[['parent department','department','IC','VMC','BC']])
    for row_i in range(subdepts.shape[0]):
        st.markdown(f"#### :green[{row_i+1}. {subdepts.loc[row_i,'department']}]")
        st.markdown(f"- :blue[In Charge] : {subdepts.loc[row_i,'IC']}")
        st.caption(f" contact {subdepts.loc[row_i,'IC']}  [call](tel:{subdepts.loc[row_i,'phone']}) or  [whatsapp](https://wa.me/91{subdepts.loc[row_i,'phone']})")
        st.markdown(f"- :blue[VMC]: {subdepts.loc[row_i,'VMC']}")
        st.markdown(f"- :blue[BC]: {subdepts.loc[row_i,'BC']}")
        st.markdown(f"")      

def show_by_dev():
    st.subheader("VOICE Structure")
    st.button("Show by department",on_click=change_subpage,args=['default'])
    df_raw = fetch_data(sheetID,'departments!A1:F57')
    df = pd.DataFrame(df_raw[1:],columns=df_raw[0])

    branch1 = st.radio(" b1",options=['IC',"VMC",'BC'],label_visibility='hidden',
    horizontal=True)
    
    if branch1 == "IC":
        IC_list = df['IC'].unique().tolist()
        IC_list.sort()
        IC_list.sort(key = lambda x: len(x))
        ic_selected = st.radio("hi",options=IC_list,label_visibility='hidden')
        st.markdown('---')
        st.markdown(f'### :blue[{ic_selected}]')        
        st.write(df[df['IC']==ic_selected][['parent department','department','VMC','BC']].reset_index(drop=True))





# ---------------------- Wrapper
login_state_map = { 'showbydev':show_by_dev,
                    'default':show_departments}

def structure_main():
    if 'substate' not in st.session_state:
        # default behaviour
        show_departments()

    elif st.session_state['substate'] in login_state_map.keys():
        # directed behaviour
        login_state_map[st.session_state['substate']]()
    else:
        # exceptional
        show_departments()