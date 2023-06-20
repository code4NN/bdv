import streamlit as st

# from other_pages.loginpage import login_main
# from other_pages.feed import show_feed
# from other_pages.sadhana_card import sc_main
# from other_pages.departments import structure_main
# from other_pages.settlement import settlement_main
# from other_pages.japa_talk import jt_main
# from other_pages.article_collection import get_article_main


if 'LAYOUT' not in st.session_state:
    st.session_state['LAYOUT'] = 'centered'
elif 'state' in st.session_state:
    if st.session_state.state == 'article_collection':
        st.session_state.LAYOUT = 'wide'

st.set_page_config(page_title="BDV",
                    page_icon='📖',
                    layout=st.session_state.LAYOUT
                    )
st.markdown( """
        <style>
        # #MainMenu {visibility: hidden;}
        # footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

st.session_state['DEBUG_ERROR'] = True

# ======================================= 
if 'status_navigator' not in st.session_state:
    # for the first run create the instances of all the available pages
    # This will not run next since the condition will be false

    st.session_state['status_navigator'] = {
        'login':None,
        'feed': None, # create instance of the feed class (after importing)
        'settlement': None
    }
    # Set the landing page to login
    st.session_state['_page'] = 'login'

# run the root loop
st.session_state['status_navigator'][st.session_state['_page']].run()

st.markdown('---')
st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")












