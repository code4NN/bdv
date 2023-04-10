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

# ======================================= 
state_page_map = {'feed':show_feed,
                  'Sadhana_Card':sc_main,
                  'dept_structure':structure_main,
                  'settlement':settlement_main
                    }

if 'exp_rerun' in st.session_state:
    if st.session_state['exp_rerun']:
        st.session_state['exp_rerun'] = False
        st.experimental_rerun()

# if 'user' in st.session_state:
#     st.write(st.session_state['user'])
if 'state' not in st.session_state:
    # default behaviour
    login_main()
else :
    # directed behaviour
    try:
        state_page_map[st.session_state.state]()    
    except Exception as e:
        st.write(e)

        
        st.header("Hare Krishna Pr")
        st.header(":red[Some error occurred]")
        user = ""
        if 'user' in st.session_state:
            user = st.session_state['user']
        else:
            user = 'not logged in'
        msg = f'Hare Krishna Prabhu an error occurred with username ->>{user["name"]}<<- While (please describe the action)'.replace(" ","%20")
        def rerun(case):
            if case==1:
                st.session_state['exp_rerun'] = True
            elif case==2:
                st.session_state['state'] = 'feed'
        st.image(image='./other_pages/images/baby_Krishna_Crying.jpg',width=150)
        st.button("retry",on_click=rerun,args=[1])
        st.button("feed",on_click=rerun,args=[2])
        st.markdown(f"[report](http://wa.me/917260869161?text={msg})")



    
st.markdown('---')
st.markdown("[have feedbacks??](http://wa.me/917260869161?text=Hare%20Krishna)")
#---
# if st.session_state












