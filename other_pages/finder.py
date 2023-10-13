import streamlit as st


class lec_finder_Class:
    def __init__(self) -> None:
        
        self.page_dict = {}
        self.current_page = 
    
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)
    