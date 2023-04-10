import streamlit as st

from other_pages.japa_talk import jt_home


st.set_page_config(page_title="BDV",
                    page_icon='📖',
                    layout='centered'
                    )

jt_home()

