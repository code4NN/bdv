import streamlit as st

# import other pages
from other_pages.loginpage import page4_login
from other_pages.feed import page4_feed

if 'LAYOUT' not in st.session_state:
    st.session_state['LAYOUT'] = 'centered'
    
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

st.session_state['DEBUG_ERROR'] = False

# =======================================
DEVELOPMENT = True
DEVELOPMENT_PAGE = 'feed'

# for the first run create the instances of all the available pages
# This will not run next since the condition will be false
# also during development create instances on every run
if ('status_navigator' not in st.session_state) or DEVELOPMENT:
    st.session_state['status_navigator'] = {
        'login':page4_login(),
        'feed': page4_feed(),
        'settlement': None
    }
    # Set the landing page to login
    st.session_state['_page'] = 'login'
    if DEVELOPMENT:
        st.session_state['_page'] = DEVELOPMENT_PAGE


# run the root loop
try:
    st.session_state['status_navigator'][st.session_state['_page']].run()
except Exception as e:
    if st.session_state.DEBUG_ERROR:
        st.write(e)
    else :
        st.error("Something Went wrong :(")
        show_detailed_error = st.checkbox("Show Error",key="Show_error_debug_button")
        if show_detailed_error:  
            st.write(e)

st.markdown('---')
st.markdown("[help improve!!](http://wa.me/917260869161?text=Hare%20Krishna%20some%20suggestion)")












