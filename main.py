import streamlit as st

from other_pages.loginpage import login_main
from other_pages.feed import show_feed
from other_pages.sadhana_card import sc_main
from other_pages.departments import structure_main


st.set_page_config(page_title="BDV",
                    page_icon='📖',
                    layout='centered'
                    )
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        # footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ======================================= 
state_page_map = {'feed':show_feed,
                  'Sadhana_Card':sc_main,
                  'dept_structure':structure_main
                    }

if 'state' not in st.session_state:
    # default behaviour
    login_main()
else :
    # directed behaviour
    state_page_map[st.session_state.state]()    
    

#---
# if st.session_state












