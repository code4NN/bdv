import streamlit as st

from other_pages.loginpage import login_main
from other_pages.feed import show_feed
from other_pages.sadhana_card import sc_main
from other_pages.departments import structure_main
from other_pages.settlement import settlement_main
from other_pages.article_collection import get_article_main

if 'LAYOUT' not in st.session_state:
    st.session_state['LAYOUT'] = 'centered'

st.set_page_config(page_title="testing",
                    page_icon='📖',
                    layout=st.session_state.LAYOUT
                    )
# #MainMenu {visibility: hidden;}
hide_menu_style = """
        <style>
        # footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.session_state['DEBUG_ERROR'] = True
USER = {"password":"trinadapi","name":"Shivendra","roles":"acc_ic","group":"yud","settlement_id":"32"}
# ======================================= 
state_page_map = {'feed':show_feed,
                  'Sadhana_Card':sc_main,
                  'dept_structure':structure_main,
                  'settlement':settlement_main,
                  'article_collection':get_article_main
                    }

if 'state' not in st.session_state:
    # default behaviour
    st.session_state['state'] = 'feed'
    st.session_state['user'] = USER
    st.session_state['user']['roles'] = st.session_state['user']['roles'].split(",")
    
    def goto(page):
        st.session_state.state = page

    left,middle,right = st.columns(3)
    left.button('Sadhana Card',on_click=goto,args=['Sadhana_Card'],key='sc')
    middle.button('💸 settlement',on_click=goto,args=['settlement'],key='acc')
    right.button('bdv departments',on_click=goto,args=['dept_structure'],key='dept')
    
    left.button('Feed',on_click=goto,args=['feed'],key='feed')
else :
    # directed behaviour
    try:
        state_page_map[st.session_state.state]()    
    except Exception as e:
        if st.session_state['DEBUG_ERROR']: 
            st.write(e)


    
st.markdown('---')
st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")
#---
# if st.session_state












