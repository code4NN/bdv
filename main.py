import streamlit as st

from other_pages.loginpage import login_main
from other_pages.feed import show_feed
from other_pages.sadhana_card import sc_main
from other_pages.departments import structure_main
from other_pages.settlement import settlement_main


st.set_page_config(page_title="BDV",
                    page_icon='📖',
                    layout='centered'
                    )
# #MainMenu {visibility: hidden;}
hide_menu_style = """
        <style>
        # footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.session_state['DEBUG_ERROR'] = False

# ======================================= 
state_page_map = {'feed':show_feed,
                  'Sadhana_Card':sc_main,
                  'dept_structure':structure_main,
                  'settlement':settlement_main
                    }

if 'state' not in st.session_state:
    # default behaviour
    login_main()

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












